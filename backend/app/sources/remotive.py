"""Remotive public API connector for direct remote job listings."""
import html
import logging
import re
from datetime import datetime, timezone

import httpx

from app.core.config import settings
from app.core.expansions import detect_level, expand_roles_multi
from app.schemas.job import JobCreate
from app.schemas.search import SearchFilters
from app.sources.base import BaseSource
from app.utils.url_validator import is_safe_url

logger = logging.getLogger(__name__)

API_URL = "https://remotive.com/api/remote-jobs"


def _plain_text(value: str) -> str:
    without_tags = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", html.unescape(without_tags)).strip()


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


class RemotiveSource(BaseSource):
    name = "remotive"

    async def search(self, filters: SearchFilters) -> list[JobCreate]:
        roles = filters.roles or ([filters.role] if filters.role else [])
        role_terms = expand_roles_multi(roles) or roles
        collected_at = datetime.now(timezone.utc)

        try:
            async with httpx.AsyncClient(
                timeout=settings.request_timeout,
                headers={"User-Agent": settings.user_agent, "Accept": "application/json"},
                follow_redirects=True,
            ) as client:
                response = await client.get(API_URL, params={"category": "software-dev"})
                response.raise_for_status()
                payload = response.json()
        except Exception as exc:
            logger.warning("Remotive request failed: %s", exc)
            return []

        jobs: list[JobCreate] = []
        for item in payload.get("jobs", []):
            title = item.get("title") or ""
            description = _plain_text(item.get("description") or "")
            searchable = f"{title} {description}".lower()
            if role_terms and not any(term.lower() in searchable for term in role_terms):
                continue

            url = item.get("url") or ""
            if not url or not is_safe_url(url):
                continue

            technologies = [
                skill for skill in filters.technologies if skill.lower() in searchable
            ]
            jobs.append(JobCreate(
                title=title,
                company=item.get("company_name") or "Não informada",
                location=item.get("candidate_required_location") or "Remoto",
                modality="remote",
                level=detect_level(title),
                description=description[:2000] or None,
                technologies=technologies,
                source=self.name,
                source_type="connector",
                url=url,
                apply_url=url,
                published_at=_parse_date(item.get("publication_date")),
                collected_at=collected_at,
                is_manual=False,
                external_id=str(item.get("id") or url),
                related_sources=[self.name],
            ))

        return jobs[: filters.max_results]
