"""
Tests for multi-role search functionality.
"""
import pytest
from datetime import datetime, timezone

from app.schemas.search import SearchFilters
from app.services.scoring import mandatory_reject
from app.schemas.job import JobCreate
from app.core.expansions import expand_roles_multi


def make_job(**kwargs) -> JobCreate:
    defaults = dict(
        title="DevOps Engineer",
        company="TechCo",
        location="Brasil",
        modality="remote",
        level=None,
        description="",
        technologies=[],
        source="test",
        url="https://example.com/job/1",
        apply_url="https://example.com/job/1",
        published_at=None,
        collected_at=datetime.now(timezone.utc),
        is_manual=False,
    )
    defaults.update(kwargs)
    return JobCreate(**defaults)


class TestExpandRolesMulti:
    def test_single_role_expands(self):
        result = expand_roles_multi(["devops"])
        assert len(result) > 1
        assert "DevOps" in result

    def test_multiple_roles_deduplicated(self):
        # devops and sre share some terms
        result = expand_roles_multi(["devops", "sre"])
        # Should not have duplicates
        assert len(result) == len(set(result))

    def test_empty_roles(self):
        result = expand_roles_multi([])
        assert result == []

    def test_unknown_role_returns_itself(self):
        result = expand_roles_multi(["some-unknown-role-xyz"])
        assert "some-unknown-role-xyz" in result


class TestSearchFiltersMultiRole:
    def test_roles_list_accepted(self):
        f = SearchFilters(roles=["DevOps", "Cloud Engineer"])
        assert "DevOps" in f.roles
        assert "Cloud Engineer" in f.roles

    def test_role_maps_to_roles(self):
        f = SearchFilters(role="DevOps")
        assert f.roles == ["DevOps"]
        assert f.role == "DevOps"

    def test_roles_maps_to_role(self):
        f = SearchFilters(roles=["Backend Python"])
        assert f.role == "Backend Python"

    def test_empty_roles_allowed(self):
        f = SearchFilters(roles=[])
        assert f.roles == []

    def test_location_mode_brasil_sets_location(self):
        f = SearchFilters(roles=["DevOps"], location_mode="brasil")
        assert f.location == "Brasil"

    def test_remote_latam_sets_remote(self):
        f = SearchFilters(roles=["DevOps"], location_mode="remoto_latam")
        assert f.remote is True
        assert f.accept_international is False


class TestMandatoryRejectMultiRole:
    def test_single_role_incompatible_rejects(self):
        """A full-stack job should be rejected when only DevOps is searched."""
        job = make_job(title="Full Stack Developer", url="https://example.com/1")
        filters = SearchFilters(roles=["DevOps"], levels=[])
        rejected, reason = mandatory_reject(job, filters)
        assert rejected

    def test_multi_role_keeps_compatible_job(self):
        """A full-stack job should NOT be rejected when Full Stack is one of the roles."""
        job = make_job(title="Full Stack Developer", url="https://example.com/2")
        filters = SearchFilters(roles=["DevOps", "Desenvolvedor Full Stack"], levels=[])
        rejected, reason = mandatory_reject(job, filters)
        # Full Stack is compatible with "Desenvolvedor Full Stack" role
        assert not rejected

    def test_excluded_words_still_reject(self):
        job = make_job(title="Senior DevOps Engineer", url="https://example.com/3")
        filters = SearchFilters(roles=["DevOps"], levels=[], excluded_words=["Senior"])
        rejected, reason = mandatory_reject(job, filters)
        assert rejected
        assert "Senior" in reason

    def test_required_words_still_reject(self):
        job = make_job(
            title="DevOps Engineer",
            description="Python and Docker",
            url="https://example.com/4"
        )
        filters = SearchFilters(roles=["DevOps"], levels=[], required_words=["Kubernetes"])
        rejected, reason = mandatory_reject(job, filters)
        assert rejected
