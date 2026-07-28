from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database.db import get_session
from app.models.job import Job, LinkAccess
from app.schemas.link_access import LinkAccessCreate, LinkAccessPage, LinkAccessRead
from app.services.result_normalization import normalize_url

router = APIRouter(tags=["link-accesses"])


async def record_access(payload: LinkAccessCreate, db: AsyncSession) -> LinkAccess:
    normalized = normalize_url(payload.url)
    result = await db.execute(select(LinkAccess).where(LinkAccess.normalized_url == normalized))
    access = result.scalars().first()
    now = datetime.now(timezone.utc)
    if access:
        access.original_url = payload.url
        access.last_accessed_at = now
        access.access_count += 1
        for field in ("job_id", "search_id", "title", "company", "source"):
            value = getattr(payload, field)
            if value is not None:
                setattr(access, field, value)
    else:
        access = LinkAccess(
            normalized_url=normalized,
            original_url=payload.url,
            **payload.model_dump(exclude={"url"}),
            first_accessed_at=now,
            last_accessed_at=now,
        )
    if payload.job_id:
        job_result = await db.execute(select(Job).where(Job.id == payload.job_id))
        job = job_result.scalars().first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        job.first_accessed_at = job.first_accessed_at or now
        job.last_accessed_at = now
        job.access_count += 1
        db.add(job)
    db.add(access)
    await db.commit()
    await db.refresh(access)
    return access


@router.post("/link-accesses", response_model=LinkAccessRead, status_code=201)
async def create_link_access(payload: LinkAccessCreate, db: AsyncSession = Depends(get_session)):
    return await record_access(payload, db)


@router.post("/jobs/{job_id}/access", response_model=LinkAccessRead, status_code=201)
async def access_job(job_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalars().first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return await record_access(LinkAccessCreate(
        url=job.apply_url, job_id=job.id, link_type=job.result_type,
        title=job.title, company=job.company, source=job.source, origin="job",
    ), db)


@router.get("/link-accesses", response_model=LinkAccessPage)
async def list_link_accesses(
    search: Optional[str] = None,
    link_type: Optional[str] = None,
    source: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    db: AsyncSession = Depends(get_session),
):
    filters = []
    if link_type:
        filters.append(LinkAccess.link_type == link_type)
    if source:
        filters.append(LinkAccess.source == source)
    if search:
        term = f"%{search.lower()}%"
        filters.append(or_(
            func.lower(LinkAccess.title).like(term),
            func.lower(LinkAccess.company).like(term),
            func.lower(LinkAccess.original_url).like(term),
        ))
    count_stmt = select(func.count(LinkAccess.id))
    stmt = select(LinkAccess)
    for condition in filters:
        count_stmt = count_stmt.where(condition)
        stmt = stmt.where(condition)
    total = (await db.execute(count_stmt)).scalar_one()
    result = await db.execute(
        stmt.order_by(LinkAccess.last_accessed_at.desc())
        .offset((page - 1) * page_size).limit(page_size)
    )
    return LinkAccessPage(items=result.scalars().all(), total=total, page=page, page_size=page_size)


@router.delete("/link-accesses/{access_id}", status_code=204)
async def delete_link_access(access_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(LinkAccess).where(LinkAccess.id == access_id))
    access = result.scalars().first()
    if not access:
        raise HTTPException(status_code=404, detail="Access record not found")
    if access.job_id:
        job_result = await db.execute(select(Job).where(Job.id == access.job_id))
        job = job_result.scalars().first()
        if job:
            job.first_accessed_at = None
            job.last_accessed_at = None
            job.access_count = 0
            db.add(job)
    await db.delete(access)
    await db.commit()


@router.delete("/link-accesses", status_code=204)
async def clear_link_accesses(db: AsyncSession = Depends(get_session)):
    accesses = (await db.execute(select(LinkAccess))).scalars().all()
    jobs = (await db.execute(select(Job).where(Job.access_count > 0))).scalars().all()
    for access in accesses:
        await db.delete(access)
    for job in jobs:
        job.first_accessed_at = None
        job.last_accessed_at = None
        job.access_count = 0
        db.add(job)
    await db.commit()
