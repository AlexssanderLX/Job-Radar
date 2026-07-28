import asyncio
import logging
import time
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.expansions import expand_roles_multi, expand_levels
from app.models.job import Job, SearchHistory
from app.schemas.job import JobCreate
from app.schemas.search import SearchFilters, SearchResult
from app.services.deduplication import deduplicate_jobs
from app.services.scoring import calculate_match_score, mandatory_reject
from app.sources.greenhouse import GreenhouseSource
from app.sources.lever import LeverSource
from app.sources.gupy import GupySource
from app.sources.github import GitHubSource
from app.sources.manual_search import ManualSearchSource
from app.sources.web_search import IndexedWebSearchSource

logger = logging.getLogger(__name__)

ALL_SOURCES = [
    GreenhouseSource(),
    LeverSource(),
    GupySource(),
    GitHubSource(),
    IndexedWebSearchSource(),
    ManualSearchSource(),
]

SOURCE_MAP = {s.name: s for s in ALL_SOURCES}


async def run_search(filters: SearchFilters, db: AsyncSession) -> SearchResult:
    start = time.monotonic()

    active_source_names = filters.sources if filters.sources else list(SOURCE_MAP.keys())
    active_sources = [SOURCE_MAP[n] for n in active_source_names if n in SOURCE_MAP]

    # Expand all roles together
    roles_to_expand = filters.roles if filters.roles else ([filters.role] if filters.role else [])
    role_variants = expand_roles_multi(roles_to_expand)
    if not role_variants:
        role_variants = roles_to_expand

    level_variants: list[str] = []
    for lvl in filters.levels:
        level_variants.extend(expand_levels(lvl))

    raw_jobs: list[JobCreate] = []
    failed_sources: list[str] = []
    searched_sources: list[str] = []
    source_progress: list[dict] = []

    async def fetch_source(source):
        source_start = time.monotonic()
        try:
            jobs = await source.search(filters)
            return source.name, jobs, None, time.monotonic() - source_start, source.is_manual
        except Exception as e:
            logger.warning("Source %s failed: %s", source.name, e)
            return source.name, [], str(e), time.monotonic() - source_start, source.is_manual

    results = await asyncio.gather(*[fetch_source(s) for s in active_sources])

    for name, jobs, error, source_duration, is_manual in results:
        searched_sources.append(name)
        source_progress.append({
            "source": name,
            "status": "error" if error else ("manual" if is_manual else ("completed" if jobs else "empty")),
            "result_count": len(jobs),
            "duration_seconds": round(source_duration, 2),
            "error": error,
        })
        if error:
            failed_sources.append(name)
        else:
            raw_jobs.extend(jobs)

    total_raw = len(raw_jobs)

    # deduplicate
    deduped = deduplicate_jobs(raw_jobs)

    # mandatory filter — applied before scoring so violating jobs never appear
    filtered: list[JobCreate] = []
    for job in deduped:
        if job.is_manual:
            filtered.append(job)
            continue
        rejected, reason = mandatory_reject(job, filters)
        if rejected:
            logger.debug("Rejected '%s': %s", job.title[:60], reason)
        else:
            filtered.append(job)

    logger.info(
        "Filter step: %d deduplicated → %d after mandatory filters",
        len(deduped), len(filtered),
    )

    # score
    scored: list[JobCreate] = []
    for job in filtered:
        if job.is_manual:
            scored.append(job)
            continue

        result = calculate_match_score(
            title=job.title,
            description=job.description or "",
            company=job.company,
            location=job.location,
            modality=job.modality,
            published_at=job.published_at,
            role_variants=role_variants,
            level_variants=level_variants,
            technologies=filters.technologies,
            location_filter=filters.location,
            remote_filter=filters.remote,
            location_mode=filters.location_mode,
            required_words=filters.required_words,
            excluded_words=filters.excluded_words,
        )
        job.match_score = result.score
        job.match_reasons = result.positives
        job.match_penalties = result.penalties
        job.match_summary = result.summary
        job.technologies = list(set(job.technologies) | set(result.techs_found))
        scored.append(job)

    # sort: manual last, then by score desc
    scored.sort(key=lambda j: (j.is_manual, -j.match_score))

    # persist to DB (upsert by URL)
    db_jobs: list[Job] = []
    now = datetime.now(timezone.utc)

    for job_data in scored:
        stmt = select(Job).where(Job.url == job_data.url)
        existing_result = await db.execute(stmt)
        existing = existing_result.scalars().first()

        if existing:
            existing.last_seen_at = now
            existing.match_score = job_data.match_score
            existing.match_reasons = job_data.match_reasons
            existing.match_penalties = job_data.match_penalties
            existing.match_summary = job_data.match_summary
            existing.technologies = job_data.technologies
            db.add(existing)
            db_jobs.append(existing)
        else:
            new_job = Job(
                **job_data.model_dump(),
                first_seen_at=now,
                last_seen_at=now,
            )
            db.add(new_job)
            db_jobs.append(new_job)

    # save search history
    duration = time.monotonic() - start
    history = SearchHistory(
        filters=filters.model_dump(),
        searched_at=now,
        total_found=len(scored),
        sources_searched=searched_sources,
        sources_failed=failed_sources,
        duration_seconds=round(duration, 2),
    )
    db.add(history)
    await db.commit()

    for job in db_jobs:
        await db.refresh(job)
    await db.refresh(history)

    from app.schemas.job import JobRead
    job_reads = []
    for j in db_jobs:
        job_reads.append(JobRead.model_validate(j))

    return SearchResult(
        search_id=history.id,
        total_raw=total_raw,
        total_deduplicated=len(deduped),
        sources_searched=searched_sources,
        sources_failed=failed_sources,
        duration_seconds=round(duration, 2),
        jobs=job_reads,
        source_progress=source_progress,
    )
