"""
Isolated, testable deduplication logic. No external calls.
"""
from difflib import SequenceMatcher
from app.schemas.job import JobCreate

SIMILARITY_THRESHOLD = 0.85

SOURCE_PRIORITY = [
    "greenhouse", "lever", "gupy", "github",
    "career_page", "manual_search",
]


def _normalize(text: str) -> str:
    return text.lower().strip()


def _title_similar(a: str, b: str) -> bool:
    ratio = SequenceMatcher(None, _normalize(a), _normalize(b)).ratio()
    return ratio >= SIMILARITY_THRESHOLD


def _source_rank(source: str) -> int:
    try:
        return SOURCE_PRIORITY.index(source.lower())
    except ValueError:
        return len(SOURCE_PRIORITY)


def _prefer(a: JobCreate, b: JobCreate) -> JobCreate:
    """Return whichever job is the better canonical record."""
    score_a = 0
    score_b = 0

    # prefer non-manual
    if not a.is_manual:
        score_a += 3
    if not b.is_manual:
        score_b += 3

    # prefer more trusted source
    if _source_rank(a.source) < _source_rank(b.source):
        score_a += 2
    else:
        score_b += 2

    # prefer richer description
    if len(a.description or "") > len(b.description or ""):
        score_a += 1
    else:
        score_b += 1

    # prefer has published_at
    if a.published_at:
        score_a += 1
    if b.published_at:
        score_b += 1

    return a if score_a >= score_b else b


def deduplicate_jobs(jobs: list[JobCreate]) -> list[JobCreate]:
    seen: list[JobCreate] = []

    for job in jobs:
        duplicate_index = None

        for i, existing in enumerate(seen):
            # same URL
            if _normalize(job.url) == _normalize(existing.url):
                duplicate_index = i
                break

            # same external_id
            if (
                job.external_id
                and existing.external_id
                and job.external_id == existing.external_id
            ):
                duplicate_index = i
                break

            # same company + very similar title
            if (
                _normalize(job.company) == _normalize(existing.company)
                and _title_similar(job.title, existing.title)
            ):
                duplicate_index = i
                break

        if duplicate_index is not None:
            seen[duplicate_index] = _prefer(seen[duplicate_index], job)
        else:
            seen.append(job)

    return seen
