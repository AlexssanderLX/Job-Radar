from datetime import datetime, timezone

from app.core.expansions import detect_level, expand_levels
from app.schemas.job import JobCreate
from app.schemas.search import SearchFilters
from app.services.scoring import mandatory_reject


def job(**values):
    defaults = dict(
        title="Backend Developer Junior", company="Acme", location="Brasil", modality="remote",
        level="Júnior", description="Python Docker", technologies=["Python", "Docker"], source="test",
        url="https://example.com/jobs/1", apply_url="https://example.com/jobs/1",
        collected_at=datetime.now(timezone.utc),
    )
    defaults.update(values)
    return JobCreate(**defaults)


def test_detects_complete_seniority_range():
    assert detect_level("Senior Backend Developer") == "Sênior"
    assert detect_level("Staff Platform Engineer") == "Staff"
    assert detect_level("Engineering Manager") == "Manager"
    assert "Principal Engineer" in expand_levels("Principal")


def test_selected_senior_level_is_accepted():
    rejected, _ = mandatory_reject(
        job(title="Senior Backend Developer", level="Sênior"),
        SearchFilters(roles=["Backend Python"], levels=["Sênior"]),
    )
    assert not rejected


def test_minimum_skill_matches_filters_job():
    filters = SearchFilters(
        roles=["Backend Python"], technologies=["Python", "Docker", "Kubernetes"], min_skill_matches=3,
    )
    rejected, reason = mandatory_reject(job(), filters)
    assert rejected
    assert "2 de 3" in reason


def test_skills_do_not_become_mandatory_without_minimum():
    filters = SearchFilters(roles=["Backend Python"], technologies=["Kubernetes"], min_skill_matches=0)
    rejected, _ = mandatory_reject(job(), filters)
    assert not rejected


def test_minimum_uses_skills_detected_from_full_source_content():
    candidate = job(
        description="Resumo curto sem a lista técnica",
        technologies=["Python", "Docker", "Kubernetes"],
    )
    filters = SearchFilters(
        roles=["Backend Python"],
        technologies=["Python", "Docker", "AWS"],
        min_skill_matches=2,
    )

    rejected, reason = mandatory_reject(candidate, filters)

    assert not rejected, reason
