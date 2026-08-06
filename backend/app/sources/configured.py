from datetime import datetime, timezone
from urllib.parse import quote

from app.models.source import Source
from app.schemas.job import JobCreate
from app.schemas.search import SearchFilters
from app.sources.base import BaseSource


class ConfiguredManualSource(BaseSource):
    """A user-configured public search link; it never scrapes or authenticates."""

    is_manual = True

    def __init__(self, config: Source):
        self.config = config
        self.name = config.name

    async def search(self, filters: SearchFilters) -> list[JobCreate]:
        if not self.config.search_url_template:
            return []
        roles = filters.roles or ([filters.role] if filters.role else [])
        query = " OR ".join(roles)
        if filters.levels:
            query += " " + " OR ".join(filters.levels)
        if filters.location:
            query += " " + filters.location
        url = self.config.search_url_template.replace("{query}", quote(query.strip()))
        return [JobCreate(
            title=f"{self.config.display_name} — {', '.join(roles) or 'Pesquisa de vagas'}",
            company=self.config.display_name,
            location=filters.location,
            modality="remote" if filters.remote else None,
            description=self.config.description or f"Pesquisa externa em {self.config.display_name}.",
            summary=self.config.description,
            source=self.name,
            source_type="manual",
            result_type="manual_search",
            url=url,
            apply_url=url,
            published_at=None,
            collected_at=datetime.now(timezone.utc),
            is_manual=True,
            related_sources=[self.name],
        )]
