"""
Gupy connector — uses the public portal search API.
Portal: https://portal.gupy.io  |  API: https://portal.gupy.io/api/job

The per-company subdomain approach (company.gupy.io) is no longer reliably public.
We use the central Gupy portal API which aggregates listings from all companies.
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
from urllib.parse import urlencode

import httpx

from app.core.config import settings
from app.core.expansions import expand_roles, expand_levels
from app.schemas.job import JobCreate
from app.schemas.search import SearchFilters
from app.sources.base import BaseSource
from app.utils.url_validator import is_safe_url

logger = logging.getLogger(__name__)

PORTAL_URL = "https://portal.gupy.io/api/job"


def _parse_date(raw: Optional[str]) -> Optional[datetime]:
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except Exception:
        return None


def _detect_modality(workplace: Optional[str]) -> str:
    if not workplace:
        return "on-site"
    w = workplace.lower()
    if "remote" in w or "remoto" in w:
        return "remote"
    if "hybrid" in w or "híbrido" in w:
        return "hybrid"
    return "on-site"


class GupySource(BaseSource):
    name = "gupy"

    async def search(self, filters: SearchFilters) -> list[JobCreate]:
        role_terms = expand_roles(filters.role)
        if not role_terms:
            role_terms = [filters.role]

        level_terms: list[str] = []
        for lvl in filters.levels:
            level_terms.extend(expand_levels(lvl))

        all_jobs: list[JobCreate] = []

        # Search with primary role term and a couple of key expansions
        search_terms = list(dict.fromkeys([filters.role] + role_terms[:3]))

        async with httpx.AsyncClient(
            timeout=settings.request_timeout,
            headers={
                "User-Agent": settings.user_agent,
                "Accept": "application/json",
                "Referer": "https://portal.gupy.io/",
            },
            follow_redirects=True,
        ) as client:
            for term in search_terms[:4]:
                jobs = await self._fetch_page(client, term, filters, level_terms)
                all_jobs.extend(jobs)

        # deduplicate by external_id within this source
        seen_ids: set[str] = set()
        unique: list[JobCreate] = []
        for j in all_jobs:
            key = j.external_id or j.url
            if key not in seen_ids:
                seen_ids.add(key)
                unique.append(j)

        return unique[: filters.max_results]

    async def _fetch_page(
        self,
        client: httpx.AsyncClient,
        term: str,
        filters: SearchFilters,
        level_terms: list[str],
    ) -> list[JobCreate]:
        params: dict = {"name": term, "limit": 40, "offset": 0}

        if filters.location and filters.location.lower() not in ("brasil", "brazil", "remoto", "remote"):
            params["city"] = filters.location

        try:
            resp = await client.get(PORTAL_URL, params=params)
            if resp.status_code in (403, 404, 429):
                logger.debug("Gupy portal %s: HTTP %s", term, resp.status_code)
                return []
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            logger.debug("Gupy portal error for '%s': %s", term, e)
            return []

        raw_jobs = data if isinstance(data, list) else data.get("data", [])
        if not isinstance(raw_jobs, list):
            raw_jobs = []

        collected_at = datetime.now(timezone.utc)
        cutoff = (
            datetime.now(timezone.utc) - timedelta(days=filters.days_ago)
            if filters.days_ago
            else None
        )
        jobs: list[JobCreate] = []

        for j in raw_jobs:
            title = j.get("name") or j.get("title", "")
            if not title:
                continue

            published_at = _parse_date(j.get("publishedDate") or j.get("createdAt"))
            if cutoff and published_at and published_at < cutoff:
                continue

            workplace = j.get("workplaceType") or j.get("type")
            modality = _detect_modality(workplace)

            if filters.remote and modality != "remote":
                continue

            if filters.location and not filters.remote:
                city = (j.get("city") or "").lower()
                state = (j.get("state") or "").lower()
                country = (j.get("country") or "").lower()
                loc_str = f"{city} {state} {country}"
                if (
                    filters.location.lower() not in loc_str
                    and modality != "remote"
                ):
                    continue

            # level filter
            if filters.levels and level_terms:
                if not any(lt.lower() in title.lower() for lt in level_terms):
                    continue

            job_id = str(j.get("id", ""))
            company_slug = j.get("companySegment") or j.get("company", {}).get("name", "")
            company_name = ""
            if isinstance(j.get("company"), dict):
                company_name = j["company"].get("name", company_slug)
            else:
                company_name = company_slug

            job_url = j.get("jobUrl") or j.get("url") or (
                f"https://portal.gupy.io/job/{job_id}" if job_id else ""
            )
            if not job_url or not is_safe_url(job_url):
                continue

            techs = [t for t in filters.technologies if t.lower() in title.lower()]
            location_str = ", ".join(filter(None, [j.get("city"), j.get("state")]))

            jobs.append(
                JobCreate(
                    title=title,
                    company=company_name or "Empresa no Gupy",
                    location=location_str or None,
                    modality=modality,
                    level=None,
                    description=j.get("description", "")[:400] or None,
                    technologies=techs,
                    source=self.name,
                    url=job_url,
                    apply_url=job_url,
                    published_at=published_at,
                    collected_at=collected_at,
                    is_manual=False,
                    external_id=job_id or None,
                )
            )

        return jobs
