"""
Lever connector.

The Lever public API (api.lever.co/v0/postings) is no longer reliably accessible
for the vast majority of companies. All tested slugs return 404.

This connector generates manual search links for jobs.lever.co via Google,
so users can find Lever-hosted jobs without requiring API access.
"""
import urllib.parse
from datetime import datetime, timezone

from app.core.expansions import expand_roles_multi, expand_levels
from app.schemas.job import JobCreate
from app.schemas.search import SearchFilters
from app.sources.base import BaseSource


def _build_google_lever_url(role_terms: list[str], level_terms: list[str], location: str | None) -> str:
    role_part = " OR ".join(f'"{t}"' for t in role_terms[:4])
    level_part = (" OR ".join(f'"{t}"' for t in level_terms[:3])) if level_terms else ""
    query = f'site:jobs.lever.co ({role_part})'
    if level_part:
        query += f' ({level_part})'
    if location:
        query += f' {location}'
    return "https://www.google.com/search?q=" + urllib.parse.quote(query)


class LeverSource(BaseSource):
    name = "lever"
    is_manual = True

    async def search(self, filters: SearchFilters) -> list[JobCreate]:
        roles_list = filters.roles if filters.roles else ([filters.role] if filters.role else [])
        role_terms = expand_roles_multi(roles_list)
        if not role_terms:
            role_terms = roles_list
        primary_role = roles_list[0] if roles_list else (filters.role or "")

        level_terms: list[str] = []
        for lvl in filters.levels:
            level_terms.extend(expand_levels(lvl))

        now = datetime.now(timezone.utc)
        url = _build_google_lever_url(role_terms, level_terms, filters.location)

        return [
            JobCreate(
                title=f"Google → Lever: {primary_role}",
                company="Google / Lever",
                location=filters.location,
                modality="remote" if filters.remote else None,
                level=", ".join(filters.levels) if filters.levels else None,
                description="Vagas em empresas que usam Lever, buscadas via Google.",
                technologies=[],
                source=self.name,
                url=url,
                apply_url=url,
                published_at=None,
                collected_at=now,
                match_score=0.0,
                is_manual=True,
            )
        ]
