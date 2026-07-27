from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, col

from app.database.db import get_session
from app.models.role import Role
from app.schemas.role import RoleCreate, RoleRead, RoleUpdate

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("", response_model=list[RoleRead])
async def list_roles(
    active: Optional[bool] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_session),
):
    stmt = select(Role)
    if active is not None:
        stmt = stmt.where(Role.active == active)
    if category:
        stmt = stmt.where(Role.category == category)
    result = await db.execute(stmt)
    roles = result.scalars().all()
    if search:
        s = search.lower()
        roles = [r for r in roles if s in r.name.lower()]
    return roles


@router.post("", response_model=RoleRead, status_code=201)
async def create_role(payload: RoleCreate, db: AsyncSession = Depends(get_session)):
    existing = await db.execute(select(Role).where(Role.name == payload.name))
    if existing.scalars().first():
        raise HTTPException(status_code=409, detail="Role with this name already exists")
    now = datetime.utcnow()
    role = Role(**payload.model_dump(), created_at=now, updated_at=now)
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role


@router.get("/{role_id}", response_model=RoleRead)
async def get_role(role_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalars().first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.patch("/{role_id}", response_model=RoleRead)
async def update_role(
    role_id: int, payload: RoleUpdate, db: AsyncSession = Depends(get_session)
):
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalars().first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    data = payload.model_dump(exclude_none=True)
    for k, v in data.items():
        setattr(role, k, v)
    role.updated_at = datetime.utcnow()
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role


@router.delete("/{role_id}", status_code=204)
async def delete_role(role_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalars().first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    await db.delete(role)
    await db.commit()
