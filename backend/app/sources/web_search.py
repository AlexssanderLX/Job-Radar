"""Optional indexed web-search source.

Serper is supported as the first adapter, but the provider-neutral protocol keeps
query generation and result normalization independent from that service.
"""
import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import settings
from app.core.expansions import expand_levels, expand_roles_multi
from app.schemas.job import JobCreate
from app.schemas.search import SearchFilters
from app.services.result_normalization import normalize_web_result
from app.sources.base import BaseSource


@dataclass
class WebResult:
    title: str
    url: str
    snippet: str = ""


class WebSearchProvider(ABC):
    provider_name: str

    @property
    @abstractmethod
    def is_configured(self) -> bool: ...

    @abstractmethod
    async def search(self, query: str, limit: int, language: str = "pt-br") -> list[WebResult]: ...

    async def health_check(self) -> bool:
        return self.is_configured


class SerperWebSearchProvider(WebSearchProvider):
    provider_name = "serper"

    def __init__(self, api_key: str = "", endpoint: str = "", client: httpx.AsyncClient | None = None):
        self.api_key = api_key
        self.endpoint = endpoint or settings.web_search_endpoint
        self.client = client

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key.strip())

    @staticmethod
    def normalize_response(payload: dict[str, Any], limit: int) -> list[WebResult]:
        results = []
        for item in payload.get("organic", [])[:limit]:
            title, link = item.get("title"), item.get("link")
            if title and link:
                results.append(WebResult(title=title, url=link, snippet=item.get("snippet", "")))
        return results

    async def search(self, query: str, limit: int, language: str = "pt-br") -> list[WebResult]:
        if not self.is_configured:
            return []
        owns_client = self.client is None
        client = self.client or httpx.AsyncClient(timeout=settings.request_timeout, follow_redirects=False)
        try:
            response = await client.post(
                self.endpoint,
                headers={"X-API-KEY": self.api_key, "Content-Type": "application/json"},
                json={"q": query, "num": min(limit, 20), "gl": "br", "hl": language},
            )
            response.raise_for_status()
            return self.normalize_response(response.json(), limit)
        finally:
            if owns_client:
                await client.aclose()


def build_web_queries(filters: SearchFilters) -> list[str]:
    roles = filters.roles or ([filters.role] if filters.role else [])
    variants = expand_roles_multi(roles) or roles
    role_part = " OR ".join(f'"{term}"' for term in variants[:6])
    levels: list[str] = []
    for level in filters.levels:
        levels.extend(expand_levels(level))
    level_part = " OR ".join(f'"{term}"' for term in list(dict.fromkeys(levels))[:4])
    suffix = f" ({level_part})" if level_part else ""
    if filters.location:
        suffix += f' "{filters.location}"'
    return [
        f"site:linkedin.com/jobs/view ({role_part}){suffix}",
        f"site:linkedin.com/posts (\"estamos contratando\" OR \"vaga aberta\" OR hiring) ({role_part})",
        f"site:gupy.io ({role_part}){suffix}",
        f"site:jobs.lever.co ({role_part}){suffix}",
        f"site:boards.greenhouse.io ({role_part}){suffix}",
    ]


class IndexedWebSearchSource(BaseSource):
    name = "web_search"

    def __init__(self, provider: WebSearchProvider | None = None):
        self.provider = provider or SerperWebSearchProvider(
            api_key=settings.web_search_api_key if settings.web_search_provider.lower() == "serper" else ""
        )

    async def search(self, filters: SearchFilters) -> list[JobCreate]:
        if not self.provider.is_configured:
            return []
        queries = build_web_queries(filters)
        per_query = max(2, min(10, filters.max_results // max(len(queries), 1)))
        batches = await asyncio.gather(
            *(self.provider.search(query, per_query) for query in queries),
            return_exceptions=True,
        )
        jobs: list[JobCreate] = []
        for query, batch in zip(queries, batches):
            if isinstance(batch, Exception):
                continue
            for item in batch:
                normalized = normalize_web_result(
                    title=item.title, url=item.url, snippet=item.snippet, query_origin=query
                )
                if normalized and normalized.result_type != "recruiter":
                    jobs.append(normalized)
        return jobs[: filters.max_results]
