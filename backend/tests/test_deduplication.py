from datetime import datetime, timezone
from app.services.deduplication import deduplicate_jobs
from app.schemas.job import JobCreate


def make_job(**overrides):
    defaults = dict(
        title="DevOps Engineer",
        company="TechCo",
        location="Brasil",
        modality="remote",
        level="Júnior",
        description="desc",
        technologies=["Docker"],
        source="greenhouse",
        url="https://example.com/job/1",
        apply_url="https://example.com/apply/1",
        published_at=datetime.now(timezone.utc),
        collected_at=datetime.now(timezone.utc),
        is_manual=False,
        external_id="ext-1",
    )
    defaults.update(overrides)
    return JobCreate(**defaults)


def test_exact_url_deduplication():
    j1 = make_job()
    j2 = make_job(source="lever")
    result = deduplicate_jobs([j1, j2])
    assert len(result) == 1


def test_same_external_id():
    j1 = make_job(external_id="abc", url="https://a.com/1")
    j2 = make_job(external_id="abc", url="https://a.com/2")
    result = deduplicate_jobs([j1, j2])
    assert len(result) == 1


def test_similar_title_same_company():
    j1 = make_job(title="DevOps Engineer Junior", url="https://a.com/1", external_id="1")
    j2 = make_job(title="DevOps Engineer Júnior", url="https://a.com/2", external_id="2")
    result = deduplicate_jobs([j1, j2])
    assert len(result) == 1


def test_different_company_kept():
    j1 = make_job(company="TechA", url="https://a.com/1", external_id="1")
    j2 = make_job(company="TechB", url="https://b.com/1", external_id="2")
    result = deduplicate_jobs([j1, j2])
    assert len(result) == 2


def test_no_false_positive_different_titles():
    j1 = make_job(title="Backend Python Developer", url="https://a.com/1", external_id="1")
    j2 = make_job(title="Cloud Security Engineer", url="https://a.com/2", external_id="2")
    result = deduplicate_jobs([j1, j2])
    assert len(result) == 2


def test_empty_list():
    assert deduplicate_jobs([]) == []


def test_prefer_non_manual():
    j1 = make_job(is_manual=True, source="manual_search", url="https://a.com/1")
    j2 = make_job(is_manual=False, source="greenhouse", url="https://a.com/1")
    result = deduplicate_jobs([j1, j2])
    assert len(result) == 1
    assert result[0].is_manual is False
