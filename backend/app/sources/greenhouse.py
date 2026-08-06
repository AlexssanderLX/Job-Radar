"""
Greenhouse public Job Board API.
Searches a curated list of companies that use Greenhouse.
API docs: https://developers.greenhouse.io/job-board.html

NOTE: The Greenhouse board API exposes `updated_at`, not the original posting date.
We do NOT apply the days_ago filter here — it would discard most results since
companies rarely update individual job postings. Recency is handled by the scorer.
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional

import httpx

from app.core.config import settings
from app.core.expansions import expand_roles_multi, expand_levels
from app.schemas.job import JobCreate
from app.schemas.search import SearchFilters
from app.sources.base import BaseSource
from app.utils.url_validator import is_safe_url

logger = logging.getLogger(__name__)

# All slugs verified by health checks against boards-api.greenhouse.io.
# Sorted roughly by number of active job listings (largest first).
GREENHOUSE_COMPANIES = [
    # Large (200+ jobs)
    "databricks", "stripe", "datadog", "mongodb", "cloudflare",
    "okta", "brex", "gitlab", "fivetran", "elastic", "twilio",
    "figma", "robinhood",
    # Medium (50–200 jobs)
    "gympass", "vercel", "quintoandar", "gusto", "chainguard",
    "stone", "duolingo", "fastly", "newrelic", "amplitude",
    "discord", "mixpanel", "singlestore",
    # Smaller / niche
    "pagerduty", "mattermost", "buildkite", "planetscale",
    "circleci", "getnet", "remote", "orca",
    # More candidates (likely valid, not yet confirmed)
    "confluent", "grafana", "snyk", "lacework",
    "auth0", "digitalocean", "cloudwalk",
]

BASE_URL = "https://boards-api.greenhouse.io/v1/boards/{company}/jobs"


def _parse_date(raw: Optional[str]) -> Optional[datetime]:
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except Exception:
        return None


def _detect_modality(text: str) -> str:
    t = text.lower()
    if "remote" in t or "remoto" in t:
        return "remote"
    if "híbrido" in t or "hybrid" in t:
        return "hybrid"
    return "on-site"


def _detect_level(text: str) -> Optional[str]:
    # Use padded string for better word-boundary matching
    t = f" {text.lower()} "
    if any(w in t for w in [" intern", "estágio", "estagi", "internship"]):
        return "Estágio"
    if any(w in t for w in ["trainee", "programa de formação", "graduate program"]):
        return "Trainee"
    if any(w in t for w in [
        "júnior", "junior", " jr ", "jr.", "entry level", "entry-level",
        " analista i ", " desenvolvedor i ", "nível i ", "nível 1",
    ]):
        return "Júnior"
    if any(w in t for w in [
        "pleno", " mid ", " mid-level", "middle", "intermediário",
        " analista ii", " desenvolvedor ii", "nível ii", "nível 2",
    ]):
        return "Pleno"
    if any(w in t for w in [
        "senior", "sênior", " sr ", "sr.", "staff", "tech lead", "principal",
        "specialist", "especialista", "manager", "gerente", "head of",
        "architect", "coordinator",
    ]):
        return "Sênior"
    return None


def _extract_techs(text: str, wanted: list[str]) -> list[str]:
    return [t for t in wanted if t.lower() in text.lower()]


def _job_matches_query(job_data: dict, query_terms: list[str]) -> bool:
    title = job_data.get("title", "").lower()
    location = (job_data.get("location") or {}).get("name", "").lower()
    combined = f"{title} {location}"
    return any(term.lower() in combined for term in query_terms)


class GreenhouseSource(BaseSource):
    name = "greenhouse"

    async def search(self, filters: SearchFilters) -> list[JobCreate]:
        roles_list = filters.roles if filters.roles else ([filters.role] if filters.role else [])
        role_terms = expand_roles_multi(roles_list)
        if not role_terms:
            role_terms = roles_list

        level_terms: list[str] = []
        for lvl in filters.levels:
            level_terms.extend(expand_levels(lvl))

        results: list[JobCreate] = []
        sem = asyncio.Semaphore(8)

        async with httpx.AsyncClient(
            timeout=settings.request_timeout,
            headers={"User-Agent": settings.user_agent},
            follow_redirects=True,
        ) as client:
            async def bounded(company):
                async with sem:
                    return await self._fetch_company(client, company, filters, role_terms, level_terms)

            gathered = await asyncio.gather(
                *[bounded(c) for c in GREENHOUSE_COMPANIES], return_exceptions=True
            )

        for result in gathered:
            if isinstance(result, list):
                results.extend(result)
            elif isinstance(result, Exception):
                logger.debug("Greenhouse company fetch failed: %s", result)

        return results[: filters.max_results]

    async def _fetch_company(
        self,
        client: httpx.AsyncClient,
        company: str,
        filters: SearchFilters,
        role_terms: list[str],
        level_terms: list[str],
    ) -> list[JobCreate]:
        url = BASE_URL.format(company=company)
        if not is_safe_url(url):
            return []

        try:
            resp = await client.get(url)
            if resp.status_code in (404, 301, 302):
                return []
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            logger.debug("Greenhouse %s error: %s", company, e)
            return []

        jobs_raw = data.get("jobs", [])
        collected_at = datetime.now(timezone.utc)
        jobs: list[JobCreate] = []

        for job in jobs_raw:
            if not _job_matches_query(job, role_terms):
                continue

            title = job.get("title", "")
            location_obj = job.get("location") or {}
            location = location_obj.get("name")
            job_url = job.get("absolute_url", "")

            if not job_url or not is_safe_url(job_url):
                continue

            modality = _detect_modality(f"{title} {location or ''}")
            is_remote_job = modality == "remote" or "remote" in (location or "").lower()

            if filters.remote:
                # User wants remote: show all matching roles globally.
                # Most US/EU companies support remote but don't label every posting.
                # Scoring already rewards remote-labeled jobs.
                pass
            elif filters.location_mode in ("estado", "cidade") and filters.location:
                # User wants a specific location (not remote-only).
                # Show jobs in that location OR globally-remote jobs.
                loc_lower = (location or "").lower()
                location_matches = filters.location.lower() in loc_lower
                if not location_matches and not is_remote_job:
                    continue

            level = _detect_level(title)

            # Pre-filter by level at fetch time to reduce volume (mandatory_reject is definitive)
            if filters.levels and level is not None and level not in filters.levels:
                continue

            # Use updated_at for display; do NOT apply days_ago (see module docstring)
            pub_raw = job.get("updated_at") or job.get("created_at")
            published_at = _parse_date(pub_raw)

            company_display = company.replace("-", " ").title()

            techs = _extract_techs(
                f"{title} {job.get('content', '')}",
                filters.technologies,
            )

            jobs.append(
                JobCreate(
                    title=title,
                    company=company_display,
                    location=location,
                    modality=modality,
                    level=level,
                    description=None,
                    technologies=techs,
                    source=self.name,
                    url=job_url,
                    apply_url=job_url,
                    published_at=published_at,
                    collected_at=collected_at,
                    is_manual=False,
                    external_id=str(job.get("id", "")),
                )
            )

        return jobs
