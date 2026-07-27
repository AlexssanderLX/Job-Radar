from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database.db import get_session
from app.models.skill import Skill
from app.schemas.skill import SkillCreate, SkillRead, SkillUpdate

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("", response_model=list[SkillRead])
async def list_skills(
    active: Optional[bool] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_session),
):
    stmt = select(Skill)
    if active is not None:
        stmt = stmt.where(Skill.active == active)
    if category:
        stmt = stmt.where(Skill.category == category)
    result = await db.execute(stmt)
    skills = result.scalars().all()
    if search:
        s = search.lower()
        skills = [sk for sk in skills if s in sk.name.lower()]
    return skills


@router.post("", response_model=SkillRead, status_code=201)
async def create_skill(payload: SkillCreate, db: AsyncSession = Depends(get_session)):
    existing = await db.execute(select(Skill).where(Skill.name == payload.name))
    if existing.scalars().first():
        raise HTTPException(status_code=409, detail="Skill with this name already exists")
    now = datetime.utcnow()
    skill = Skill(**payload.model_dump(), created_at=now, updated_at=now)
    db.add(skill)
    await db.commit()
    await db.refresh(skill)
    return skill


@router.get("/{skill_id}", response_model=SkillRead)
async def get_skill(skill_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Skill).where(Skill.id == skill_id))
    skill = result.scalars().first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


@router.patch("/{skill_id}", response_model=SkillRead)
async def update_skill(
    skill_id: int, payload: SkillUpdate, db: AsyncSession = Depends(get_session)
):
    result = await db.execute(select(Skill).where(Skill.id == skill_id))
    skill = result.scalars().first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    data = payload.model_dump(exclude_none=True)
    for k, v in data.items():
        setattr(skill, k, v)
    skill.updated_at = datetime.utcnow()
    db.add(skill)
    await db.commit()
    await db.refresh(skill)
    return skill


@router.delete("/{skill_id}", status_code=204)
async def delete_skill(skill_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Skill).where(Skill.id == skill_id))
    skill = result.scalars().first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    await db.delete(skill)
    await db.commit()
