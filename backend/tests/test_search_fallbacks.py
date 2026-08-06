from unittest.mock import AsyncMock, Mock
from datetime import datetime, timezone

import pytest

from app.schemas.search import SearchFilters
from app.schemas.job import JobCreate
from app.services.search_service import keep_manual_fallbacks
from app.sources.gupy import GupySource
from app.sources.web_search import build_web_queries


@pytest.mark.asyncio
async def test_gupy_brazil_wide_does_not_send_city_parameter():
    source = GupySource()
    response = Mock(status_code=200)
    response.raise_for_status = Mock()
    response.json.return_value = {"data": []}
    client = AsyncMock()
    client.get.return_value = response

    filters = SearchFilters(roles=["Backend"], location="Brasil", location_mode="brasil")
    await source._fetch_page(client, "Backend", filters, [])

    assert "city" not in client.get.await_args.kwargs["params"]


def test_unknown_levels_are_included_by_default():
    filters = SearchFilters(roles=["Backend"], levels=["Júnior", "Pleno"])
    assert filters.include_unlevel is True


def test_international_queries_are_not_restricted_to_brazil():
    filters = SearchFilters(
        roles=["Backend"],
        location="Brasil",
        location_mode="brasil_internacional",
    )
    assert all('"Brasil"' not in query for query in build_web_queries(filters))


def _job(url: str, manual: bool) -> JobCreate:
    return JobCreate(
        title="Backend Júnior",
        company="Empresa",
        source="test",
        url=url,
        apply_url=url,
        is_manual=manual,
        collected_at=datetime.now(timezone.utc),
    )


def test_manual_searches_are_hidden_when_an_automatic_job_exists():
    automatic = _job("https://example.com/job", False)
    manual = _job("https://example.com/search", True)
    assert keep_manual_fallbacks([automatic, manual]) == [automatic]


def test_manual_searches_remain_when_no_automatic_job_exists():
    manual = _job("https://example.com/search", True)
    assert keep_manual_fallbacks([manual]) == [manual]
