import pytest

from app.models.source import Source
from app.schemas.search import SearchFilters
from app.schemas.source import SourceCreate
from app.sources.configured import ConfiguredManualSource


def test_source_template_rejects_private_url():
    with pytest.raises(ValueError):
        SourceCreate(
            name="unsafe", display_name="Unsafe", source_type="manual", is_manual=True,
            search_url_template="http://127.0.0.1/search?q={query}",
        )


def test_source_template_requires_query_placeholder():
    with pytest.raises(ValueError):
        SourceCreate(
            name="linkedin", display_name="LinkedIn", source_type="manual", is_manual=True,
            search_url_template="https://www.linkedin.com/jobs/search/",
        )


@pytest.mark.asyncio
async def test_configured_linkedin_generates_filtered_search():
    source = Source(
        name="linkedin", display_name="LinkedIn Jobs", source_type="manual", is_manual=True,
        search_url_template="https://www.linkedin.com/jobs/search/?keywords={query}", active=True,
    )
    results = await ConfiguredManualSource(source).search(
        SearchFilters(roles=["DevOps", "Cloud Engineer"], levels=["Júnior"], location="Brasil")
    )
    assert len(results) == 1
    assert results[0].source == "linkedin"
    assert results[0].is_manual is True
    assert "DevOps%20OR%20Cloud%20Engineer" in results[0].url


@pytest.mark.asyncio
async def test_source_crud_accepts_linkedin(client):
    response = await client.post("/api/sources", json={
        "name": "linkedin", "display_name": "LinkedIn Jobs", "source_type": "manual",
        "is_manual": True, "active": True, "priority": 6, "domain": "linkedin.com",
        "search_url_template": "https://www.linkedin.com/jobs/search/?keywords={query}",
    })
    assert response.status_code == 201
    assert response.json()["domain"] == "linkedin.com"
