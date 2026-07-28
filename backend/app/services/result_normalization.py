"""Deterministic normalization for public search results.

This module never fetches URLs and never invents missing fields. It converts the
small, provider-neutral web result shape into the canonical JobCreate schema.
"""
import html
import re
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from app.schemas.job import JobCreate

TRACKING_PARAMS = {
    "fbclid", "gclid", "msclkid", "ref", "referrer",
    "utm_campaign", "utm_content", "utm_medium", "utm_source", "utm_term",
}
JOB_PATH_SIGNALS = ("/jobs/view/", "/jobs/", "/job/", "/careers/", "/positions/", "/vagas/")
JOB_WORDS = ("vaga", "developer", "desenvolvedor", "engineer", "engenheiro", "analista", "estágio", "estagio", "intern")
HIRING_WORDS = ("estamos contratando", "está contratando", "esta contratando", "vaga aberta", "hiring", "oportunidade")


def normalize_url(url: str) -> str:
    parts = urlsplit(url.strip())
    host = (parts.hostname or "").lower()
    port = f":{parts.port}" if parts.port and parts.port not in (80, 443) else ""
    path = re.sub(r"/+$", "", parts.path) or "/"
    query = urlencode(sorted(
        (key, value) for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if key.lower() not in TRACKING_PARAMS and not key.lower().startswith("utm_")
    ))
    return urlunsplit((parts.scheme.lower(), host + port, path, query, ""))


def sanitize_summary(value: Optional[str], limit: int = 240) -> Optional[str]:
    if not value:
        return None
    text = html.unescape(re.sub(r"<[^>]+>", " ", value))
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return None
    if len(text) <= limit:
        return text
    shortened = text[: limit + 1].rsplit(" ", 1)[0].rstrip(" ,.;:")
    return shortened + "…"


def classify_result(url: str, title: str, snippet: str = "") -> str:
    url_lower = url.lower()
    text = f"{title} {snippet}".lower()
    if "linkedin.com/in/" in url_lower:
        return "recruiter"
    if "linkedin.com/posts/" in url_lower:
        return "hiring_post" if any(word in text for word in HIRING_WORDS) else "irrelevant"
    if any(signal in url_lower for signal in JOB_PATH_SIGNALS):
        return "job"
    if any(word in text for word in HIRING_WORDS) and any(word in text for word in JOB_WORDS):
        return "hiring_post"
    if "/careers" in url_lower or "carreiras" in text:
        return "career_page"
    if any(word in text for word in JOB_WORDS):
        return "job"
    return "irrelevant"


def source_from_url(url: str) -> str:
    lowered = url.lower()
    if "linkedin.com/jobs/view/" in lowered:
        return "linkedin_jobs"
    if "linkedin.com/posts/" in lowered:
        return "linkedin_post"
    if "gupy.io" in lowered:
        return "gupy"
    if "jobs.lever.co" in lowered:
        return "lever"
    if "greenhouse.io" in lowered:
        return "greenhouse"
    return (urlsplit(url).hostname or "web").lower().removeprefix("www.")


def extract_company(title: str, source: str) -> Optional[str]:
    for separator in (" | ", " - ", " – ", " — "):
        parts = [part.strip() for part in title.split(separator) if part.strip()]
        if len(parts) >= 2:
            candidate = parts[-1]
            if candidate.lower() not in {"linkedin", "gupy", "lever", "greenhouse"}:
                return candidate[:160]
    match = re.match(r"(.+?)\s+(?:está contratando|is hiring)", title, re.IGNORECASE)
    return match.group(1).strip()[:160] if match else None


def normalize_web_result(
    *,
    title: str,
    url: str,
    snippet: str = "",
    published_at: Optional[datetime] = None,
    query_origin: Optional[str] = None,
) -> Optional[JobCreate]:
    result_type = classify_result(url, title, snippet)
    if result_type == "irrelevant":
        return None
    source = source_from_url(url)
    normalized_url = normalize_url(url)
    return JobCreate(
        title=title.strip(),
        company=extract_company(title, source) or "Não informada",
        description=sanitize_summary(snippet),
        summary=sanitize_summary(snippet),
        source=source,
        source_type="web_search",
        result_type=result_type,
        url=normalized_url,
        apply_url=normalized_url,
        published_at=published_at,
        collected_at=datetime.now(timezone.utc),
        query_origin=query_origin,
        raw_title=title,
        raw_snippet=snippet or None,
        is_manual=False,
        related_sources=[source],
    )
