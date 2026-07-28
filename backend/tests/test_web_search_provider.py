import pytest

from app.schemas.search import SearchFilters
from app.sources.web_search import (
    IndexedWebSearchSource,
    SerperWebSearchProvider,
    WebResult,
    WebSearchProvider,
    build_web_queries,
)


class FakeProvider(WebSearchProvider):
    provider_name = "fake"
    is_configured = True

    async def search(self, query: str, limit: int, language: str = "pt-br"):
        if "posts" in query:
            return [WebResult("Acme está contratando Backend", "https://linkedin.com/posts/acme-1", "Vaga aberta para Python")]
        return [WebResult("Backend Developer - Acme", "https://linkedin.com/jobs/view/123?utm_source=test", "Python e Docker")]


@pytest.mark.asyncio
async def test_unconfigured_provider_does_not_call_network():
    provider = SerperWebSearchProvider(api_key="")
    assert provider.is_configured is False
    assert await provider.search("query", 10) == []


def test_serper_response_adapter():
    items = SerperWebSearchProvider.normalize_response(
        {"organic": [{"title": "Job", "link": "https://example.com/jobs/1", "snippet": "Python"}]}, 5
    )
    assert items == [WebResult("Job", "https://example.com/jobs/1", "Python")]


def test_queries_combine_multiple_roles():
    queries = build_web_queries(SearchFilters(roles=["DevOps", "Backend Python"], levels=["Júnior"]))
    assert all("DevOps" in query or "Backend Python" in query or "Python Developer" in query for query in queries)
    assert any("linkedin.com/jobs/view" in query for query in queries)


@pytest.mark.asyncio
async def test_indexed_source_returns_individual_normalized_results():
    jobs = await IndexedWebSearchSource(FakeProvider()).search(
        SearchFilters(roles=["Backend Python"], max_results=20)
    )
    assert jobs
    assert all(not job.is_manual for job in jobs)
    assert {job.result_type for job in jobs} == {"job", "hiring_post"}
    assert jobs[0].url == "https://linkedin.com/jobs/view/123"
