from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database.db import get_session
from app.models.stack import Stack, StackSkill
from app.schemas.stack import StackCreate, StackRead, StackUpdate

router = APIRouter(prefix="/stacks", tags=["stacks"])


async def _get_stack_skill_ids(db: AsyncSession, stack_id: int) -> list[int]:
    result = await db.execute(select(StackSkill).where(StackSkill.stack_id == stack_id))
    return [ss.skill_id for ss in result.scalars().all()]


@router.get("", response_model=list[StackRead])
async def list_stacks(db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Stack))
    stacks = result.scalars().all()
    out = []
    for stack in stacks:
        skill_ids = await _get_stack_skill_ids(db, stack.id)
        out.append(StackRead(
            id=stack.id,
            name=stack.name,
            description=stack.description,
            active=stack.active,
            created_at=stack.created_at,
            updated_at=stack.updated_at,
            skill_ids=skill_ids,
        ))
    return out


@router.post("", response_model=StackRead, status_code=201)
async def create_stack(payload: StackCreate, db: AsyncSession = Depends(get_session)):
    existing = await db.execute(select(Stack).where(Stack.name == payload.name))
    if existing.scalars().first():
        raise HTTPException(status_code=409, detail="Stack with this name already exists")
    now = datetime.utcnow()
    stack = Stack(
        name=payload.name,
        description=payload.description,
        active=payload.active,
        created_at=now,
        updated_at=now,
    )
    db.add(stack)
    await db.commit()
    await db.refresh(stack)
    for skill_id in payload.skills:
        db.add(StackSkill(stack_id=stack.id, skill_id=skill_id))
    await db.commit()
    skill_ids = await _get_stack_skill_ids(db, stack.id)
    return StackRead(
        id=stack.id,
        name=stack.name,
        description=stack.description,
        active=stack.active,
        created_at=stack.created_at,
        updated_at=stack.updated_at,
        skill_ids=skill_ids,
    )


@router.get("/{stack_id}", response_model=StackRead)
async def get_stack(stack_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Stack).where(Stack.id == stack_id))
    stack = result.scalars().first()
    if not stack:
        raise HTTPException(status_code=404, detail="Stack not found")
    skill_ids = await _get_stack_skill_ids(db, stack_id)
    return StackRead(
        id=stack.id,
        name=stack.name,
        description=stack.description,
        active=stack.active,
        created_at=stack.created_at,
        updated_at=stack.updated_at,
        skill_ids=skill_ids,
    )


@router.patch("/{stack_id}", response_model=StackRead)
async def update_stack(
    stack_id: int, payload: StackUpdate, db: AsyncSession = Depends(get_session)
):
    result = await db.execute(select(Stack).where(Stack.id == stack_id))
    stack = result.scalars().first()
    if not stack:
        raise HTTPException(status_code=404, detail="Stack not found")
    data = payload.model_dump(exclude_none=True)
    skills = data.pop("skills", None)
    for k, v in data.items():
        setattr(stack, k, v)
    stack.updated_at = datetime.utcnow()
    db.add(stack)
    if skills is not None:
        existing = await db.execute(select(StackSkill).where(StackSkill.stack_id == stack_id))
        for ss in existing.scalars().all():
            await db.delete(ss)
        for skill_id in skills:
            db.add(StackSkill(stack_id=stack_id, skill_id=skill_id))
    await db.commit()
    await db.refresh(stack)
    skill_ids = await _get_stack_skill_ids(db, stack_id)
    return StackRead(
        id=stack.id,
        name=stack.name,
        description=stack.description,
        active=stack.active,
        created_at=stack.created_at,
        updated_at=stack.updated_at,
        skill_ids=skill_ids,
    )


@router.delete("/{stack_id}", status_code=204)
async def delete_stack(stack_id: int, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Stack).where(Stack.id == stack_id))
    stack = result.scalars().first()
    if not stack:
        raise HTTPException(status_code=404, detail="Stack not found")
    existing = await db.execute(select(StackSkill).where(StackSkill.stack_id == stack_id))
    for ss in existing.scalars().all():
        await db.delete(ss)
    await db.delete(stack)
    await db.commit()
