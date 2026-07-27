from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, desc

from app.database.db import get_session
from app.models.job import Job, SearchHistory, SavedFilter
from app.schemas.job import JobRead, JobUpdate
from app.schemas.search import (
    SavedFilterCreate,
    SavedFilterRead,
    SearchFilters,
    SearchHistoryRead,
    SearchResult,
)
from app.services.search_service import run_search, SOURCE_MAP
from app.api.roles import router as roles_router
from app.api.skills import router as skills_router
from app.api.stacks import router as stacks_router
from app.api.search_profiles import router as profiles_router
from app.api.sources import router as sources_router
from app.api.dashboard import router as dashboard_router

router = APIRouter()

# Include sub-routers
router.include_router(roles_router)
router.include_router(skills_router)
router.include_router(stacks_router)
router.include_router(profiles_router)
router.include_router(sources_router)
router.include_router(dashboard_router)


@router.post("/search", response_model=SearchResult)
async def search_jobs(
    filters: SearchFilters,
    db: AsyncSession = Depends(get_session),
):
    return await run_search(filters, db)


@router.get("/jobs", response_model=list[JobRead])
async def list_jobs(
    source: Optional[str] = None,
    min_score: Optional[float] = None,
    remote: Optional[bool] = None,
    is_favorite: Optional[bool] = None,
    is_hidden: Optional[bool] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(default=200, le=500),
    db: AsyncSession = Depends(get_session),
):
    stmt = select(Job).order_by(desc(Job.match_score))
    if source:
        stmt = stmt.where(Job.source == source)
    if min_score is not None:
        stmt = stmt.where(Job.match_score >= min_score)
    if remote is not None:
        if remote:
            stmt = stmt.where(Job.modality == "remote")
    if is_favorite is not None:
        stmt = stmt.where(Job.is_favorite == is_favorite)
    if is_hidden is not None:
        stmt = stmt.where(Job.is_hidden == is_hidden)
    else:
        stmt = stmt.where(Job.is_hidden == False)
    if status:
        stmt = stmt.where(Job.status == status)

    stmt = stmt.limit(limit)
    result = await db.execute(stmt)
    jobs = result.scalars().all()

    if search:
        s = search.lower()
        jobs = [j for j in jobs if s in j.title.lower() or s in j.company.lower()]

    return jobs


@router.get("/jobs/{job_id}", response_model=JobRead)
async def get_job(job_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalars().first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.patch("/jobs/{job_id}", response_model=JobRead)
async def update_job(
    job_id: int,
    update: JobUpdate,
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalars().first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    data = update.model_dump(exclude_none=True)
    for k, v in data.items():
        setattr(job, k, v)
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job


@router.delete("/jobs/{job_id}", status_code=204)
async def delete_job(job_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalars().first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    await db.delete(job)
    await db.commit()


@router.get("/searches", response_model=list[SearchHistoryRead])
async def list_searches(
    limit: int = Query(default=50, le=200),
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(
        select(SearchHistory).order_by(desc(SearchHistory.searched_at)).limit(limit)
    )
    return result.scalars().all()


@router.post("/saved-filters", response_model=SavedFilterRead)
async def create_saved_filter(
    payload: SavedFilterCreate,
    db: AsyncSession = Depends(get_session),
):
    sf = SavedFilter(name=payload.name, filters=payload.filters.model_dump())
    db.add(sf)
    await db.commit()
    await db.refresh(sf)
    return sf


@router.get("/saved-filters", response_model=list[SavedFilterRead])
async def list_saved_filters(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(SavedFilter).order_by(desc(SavedFilter.created_at)))
    rows = result.scalars().all()
    out = []
    for sf in rows:
        try:
            filters = SearchFilters(**sf.filters)
        except Exception:
            filters = SearchFilters(roles=[], role=None)
        out.append(
            SavedFilterRead(
                id=sf.id,
                name=sf.name,
                filters=filters,
                created_at=sf.created_at,
                updated_at=sf.updated_at,
            )
        )
    return out


@router.delete("/saved-filters/{filter_id}", status_code=204)
async def delete_saved_filter(
    filter_id: int,
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(select(SavedFilter).where(SavedFilter.id == filter_id))
    sf = result.scalars().first()
    if not sf:
        raise HTTPException(status_code=404, detail="Filter not found")
    await db.delete(sf)
    await db.commit()


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "sources": list(SOURCE_MAP.keys()),
        "manual_sources": [n for n, s in SOURCE_MAP.items() if s.is_manual],
    }
