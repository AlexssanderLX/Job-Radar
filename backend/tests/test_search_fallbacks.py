from unittest.mock import AsyncMock, Mock

import pytest

from app.schemas.search import SearchFilters
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
