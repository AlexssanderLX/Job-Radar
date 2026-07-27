from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, text
from sqlmodel import select, desc

from app.database.db import get_session
from app.models.job import Job, SearchHistory
from app.models.role import Role
from app.models.search_profile import SearchProfile
from app.models.source import Source
from app.schemas.job import JobRead
from app.schemas.search import SearchHistoryRead

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("")
async def get_dashboard(db: AsyncSession = Depends(get_session)):
    # Job counts
    total_result = await db.execute(select(func.count(Job.id)))
    total_jobs = total_result.scalar() or 0

    new_result = await db.execute(select(func.count(Job.id)).where(Job.status == "new"))
    new_jobs = new_result.scalar() or 0

    fav_result = await db.execute(select(func.count(Job.id)).where(Job.is_favorite == True))
    favorite_jobs = fav_result.scalar() or 0

    hidden_result = await db.execute(select(func.count(Job.id)).where(Job.is_hidden == True))
    hidden_jobs = hidden_result.scalar() or 0

    applied_result = await db.execute(select(func.count(Job.id)).where(Job.applied == True))
    applied_jobs = applied_result.scalar() or 0

    # Search counts
    searches_result = await db.execute(select(func.count(SearchHistory.id)))
    searches_count = searches_result.scalar() or 0

    # Profile counts
    profiles_result = await db.execute(select(func.count(SearchProfile.id)).where(SearchProfile.active == True))
    profiles_count = profiles_result.scalar() or 0

    # Source counts
    sources_result = await db.execute(select(func.count(Source.id)).where(Source.active == True))
    sources_count = sources_result.scalar() or 0

    # Recent jobs (last 10, not hidden)
    recent_result = await db.execute(
        select(Job)
        .where(Job.is_hidden == False)
        .order_by(desc(Job.first_seen_at))
        .limit(10)
    )
    recent_jobs_raw = recent_result.scalars().all()
    recent_jobs = [JobRead.model_validate(j) for j in recent_jobs_raw]

    # Top jobs (highest score, last 5, not hidden)
    top_result = await db.execute(
        select(Job)
        .where(Job.is_hidden == False)
        .where(Job.is_manual == False)
        .order_by(desc(Job.match_score))
        .limit(5)
    )
    top_jobs_raw = top_result.scalars().all()
    top_jobs = [JobRead.model_validate(j) for j in top_jobs_raw]

    # Recent searches (last 5)
    searches_recent_result = await db.execute(
        select(SearchHistory).order_by(desc(SearchHistory.searched_at)).limit(5)
    )
    recent_searches_raw = searches_recent_result.scalars().all()
    recent_searches = [SearchHistoryRead.model_validate(s) for s in recent_searches_raw]

    # By source
    by_source_result = await db.execute(
        select(Job.source, func.count(Job.id)).group_by(Job.source)
    )
    by_source = {row[0]: row[1] for row in by_source_result.all()}

    # By level
    by_level_result = await db.execute(
        select(Job.level, func.count(Job.id)).where(Job.level != None).group_by(Job.level)
    )
    by_level = {row[0]: row[1] for row in by_level_result.all()}

    return {
        "total_jobs": total_jobs,
        "new_jobs": new_jobs,
        "favorite_jobs": favorite_jobs,
        "hidden_jobs": hidden_jobs,
        "applied_jobs": applied_jobs,
        "searches_count": searches_count,
        "profiles_count": profiles_count,
        "sources_count": sources_count,
        "recent_jobs": recent_jobs,
        "top_jobs": top_jobs,
        "recent_searches": recent_searches,
        "by_source": by_source,
        "by_level": by_level,
    }
