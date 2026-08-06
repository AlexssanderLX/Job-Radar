"""Remote OK public JSON feed connector."""
import html
import logging
import re
from datetime import datetime, timezone

import httpx

from app.core.config import settings
from app.core.expansions import detect_level, matches_role_text
from app.schemas.job import JobCreate
from app.schemas.search import SearchFilters
from app.sources.base import BaseSource
from app.utils.url_validator import is_safe_url

logger = logging.getLogger(__name__)
API_URL = "https://remoteok.com/api"


def _plain_text(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


class RemoteOkSource(BaseSource):
    name = "remoteok"

    async def search(self, filters: SearchFilters) -> list[JobCreate]:
        roles = filters.roles or ([filters.role] if filters.role else [])
        collected_at = datetime.now(timezone.utc)
        try:
            async with httpx.AsyncClient(
                timeout=settings.request_timeout,
                headers={"User-Agent": settings.user_agent, "Accept": "application/json"},
                follow_redirects=True,
            ) as client:
                response = await client.get(API_URL)
                response.raise_for_status()
                payload = response.json()
        except Exception as exc:
            logger.warning("Remote OK request failed: %s", exc)
            return []

        jobs: list[JobCreate] = []
        for item in payload if isinstance(payload, list) else []:
            if not isinstance(item, dict) or not item.get("id"):
                continue
            title = _plain_text(item.get("position") or "")
            description = _plain_text(item.get("description") or "")
            tags = [str(tag) for tag in (item.get("tags") or [])]
            searchable = f"{title} {description} {' '.join(tags)}".lower()
            if roles and not matches_role_text(searchable, roles):
                continue
            url = item.get("apply_url") or item.get("url") or ""
            if not title or not url or not is_safe_url(url):
                continue
            technologies = [
                skill for skill in filters.technologies if skill.lower() in searchable
            ]
            jobs.append(JobCreate(
                title=title,
                company=_plain_text(item.get("company") or "") or "Não informada",
                location=_plain_text(item.get("location") or "") or "Remoto",
                modality="remote",
                level=detect_level(title),
                description=description[:2000] or None,
                technologies=technologies,
                source=self.name,
                source_type="connector",
                url=url,
                apply_url=url,
                published_at=_parse_date(item.get("date")),
                collected_at=collected_at,
                is_manual=False,
                external_id=str(item["id"]),
                related_sources=[self.name],
            ))
        return jobs[: filters.max_results]
