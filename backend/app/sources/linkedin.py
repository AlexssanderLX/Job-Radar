"""Automatic LinkedIn public guest-jobs connector (no login required)."""
import asyncio
import logging
from datetime import datetime, timezone

import httpx
from bs4 import BeautifulSoup

from app.core.config import settings
from app.core.expansions import detect_level, expand_roles_multi
from app.schemas.job import JobCreate
from app.schemas.search import SearchFilters
from app.sources.base import BaseSource
from app.utils.url_validator import is_safe_url

logger = logging.getLogger(__name__)
SEARCH_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
DETAIL_URL = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"


def _text(node) -> str:
    return node.get_text(" ", strip=True) if node else ""


def parse_search_cards(markup: str) -> list[dict]:
    soup = BeautifulSoup(markup, "html.parser")
    results = []
    for card in soup.select(".base-search-card"):
        link = card.select_one("a.base-card__full-link")
        urn = card.get("data-entity-urn", "")
        job_id = urn.rsplit(":", 1)[-1] if urn else ""
        url = (link.get("href") or "").split("?", 1)[0] if link else ""
        title = _text(card.select_one(".base-search-card__title"))
        if not job_id or not title or not is_safe_url(url):
            continue
        time_node = card.select_one("time")
        results.append({
            "id": job_id,
            "title": title,
            "company": _text(card.select_one(".base-search-card__subtitle")) or "Não informada",
            "location": _text(card.select_one(".job-search-card__location")) or None,
            "url": url,
            "date": time_node.get("datetime") if time_node else None,
        })
    return results


def parse_job_description(markup: str) -> str:
    soup = BeautifulSoup(markup, "html.parser")
    node = soup.select_one(".show-more-less-html__markup")
    return _text(node)


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


class LinkedInSource(BaseSource):
    name = "linkedin_jobs"

    async def search(self, filters: SearchFilters) -> list[JobCreate]:
        roles = filters.roles or ([filters.role] if filters.role else [])
        location = ""
        if filters.location_mode in ("estado", "cidade", "brasil"):
            location = filters.location or "Brasil"

        page_limit = min(filters.max_results, 100)
        preferred_terms = []
        for role in roles:
            variants = expand_roles_multi([role]) or [role]
            preferred_terms.append(variants[0])
        keywords = " OR ".join(dict.fromkeys(preferred_terms or roles))
        requests = [
            {"keywords": keywords, "location": location, "start": start}
            for start in range(0, page_limit, 10)
        ]

        params_base: dict[str, str] = {}
        if filters.days_ago:
            params_base["f_TPR"] = f"r{filters.days_ago * 86400}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
        }
        try:
            async with httpx.AsyncClient(
                timeout=settings.request_timeout,
                headers=headers,
                follow_redirects=True,
            ) as client:
                search_semaphore = asyncio.Semaphore(2)

                async def fetch_search_page(request_params: dict):
                    async with search_semaphore:
                        for attempt in range(3):
                            try:
                                response = await client.get(
                                    SEARCH_URL, params={**request_params, **params_base}
                                )
                                if response.status_code != 429:
                                    return response
                                retry_after = response.headers.get("Retry-After")
                                delay = float(retry_after) if retry_after and retry_after.isdigit() else 0.75 * (attempt + 1)
                                await asyncio.sleep(min(delay, 3.0))
                            except Exception as exc:
                                if attempt == 2:
                                    return exc
                                await asyncio.sleep(0.5 * (attempt + 1))
                        return None

                pages = await asyncio.gather(*(fetch_search_page(params) for params in requests))
                cards_by_id: dict[str, dict] = {}
                for response in pages:
                    if response is None or isinstance(response, Exception) or response.status_code != 200:
                        continue
                    for card in parse_search_cards(response.text):
                        cards_by_id[card["id"]] = card

                semaphore = asyncio.Semaphore(8)

                async def detail(card: dict) -> tuple[dict, str]:
                    async with semaphore:
                        try:
                            response = await client.get(DETAIL_URL.format(job_id=card["id"]))
                            return card, parse_job_description(response.text) if response.status_code == 200 else ""
                        except Exception:
                            return card, ""

                detailed = await asyncio.gather(*(detail(card) for card in cards_by_id.values()))
        except Exception as exc:
            logger.warning("LinkedIn guest search failed: %s", exc)
            return []

        collected_at = datetime.now(timezone.utc)
        jobs = []
        for card, description in detailed:
            searchable = f"{card['title']} {description}".lower()
            technologies = [skill for skill in filters.technologies if skill.lower() in searchable]
            jobs.append(JobCreate(
                title=card["title"],
                company=card["company"],
                location=card["location"],
                modality="remote" if "remote" in searchable or "remoto" in searchable else None,
                level=detect_level(card["title"]),
                description=description[:2000] or None,
                technologies=technologies,
                source=self.name,
                source_type="connector",
                url=card["url"],
                apply_url=card["url"],
                published_at=_parse_date(card["date"]),
                collected_at=collected_at,
                is_manual=False,
                external_id=card["id"],
                related_sources=[self.name],
            ))
        return jobs[: filters.max_results]
