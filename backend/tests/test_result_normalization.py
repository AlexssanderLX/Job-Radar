from app.services.result_normalization import (
    classify_result,
    extract_company,
    normalize_url,
    normalize_web_result,
    sanitize_summary,
)


def test_normalize_url_removes_tracking_and_fragment():
    url = "https://Example.com/jobs/123/?utm_source=x&job=42#apply"
    assert normalize_url(url) == "https://example.com/jobs/123?job=42"


def test_classifies_linkedin_types():
    assert classify_result("https://linkedin.com/jobs/view/123", "Backend Developer") == "job"
    assert classify_result("https://linkedin.com/posts/a-123", "Empresa está contratando Backend") == "hiring_post"
    assert classify_result("https://linkedin.com/in/person", "Tech Recruiter") == "recruiter"


def test_irrelevant_result_is_discarded():
    assert normalize_web_result(title="Receita de bolo", url="https://example.com/bolo") is None


def test_normalizes_job_without_inventing_metadata():
    result = normalize_web_result(
        title="Backend Developer - Acme",
        url="https://jobs.lever.co/acme/123?utm_campaign=jobs",
        snippet="<b>APIs</b> com Python e Docker.",
        query_origin='site:jobs.lever.co "Backend Developer"',
    )
    assert result is not None
    assert result.company == "Acme"
    assert result.source == "lever"
    assert result.summary == "APIs com Python e Docker."
    assert result.result_type == "job"
    assert result.url == "https://jobs.lever.co/acme/123"
    assert result.location is None


def test_summary_is_plain_and_bounded():
    summary = sanitize_summary("<p>" + ("palavra " * 80) + "</p>")
    assert summary is not None
    assert "<" not in summary
    assert len(summary) <= 241


def test_company_extraction_avoids_platform_name():
    assert extract_company("Backend Developer | Acme", "linkedin_jobs") == "Acme"
    assert extract_company("Backend Developer - LinkedIn", "linkedin_jobs") is None
