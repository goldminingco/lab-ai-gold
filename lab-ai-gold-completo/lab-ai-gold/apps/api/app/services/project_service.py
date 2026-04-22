from __future__ import annotations
import uuid
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectRead


def _to_read(p: Project) -> ProjectRead:
    return ProjectRead(
        id=p.id, user_id=p.user_id, name=p.name, description=p.description,
        status=p.status, phase=p.phase, created_at=p.created_at,
        has_area=bool(p.areas),
        has_analysis=bool(p.analyses),
    )


async def create_project(data: ProjectCreate, user: User, db: AsyncSession) -> ProjectRead:
    proj = Project(user_id=user.id, name=data.name.strip(), description=data.description)
    db.add(proj)
    await db.flush()
    await db.refresh(proj)
    return _to_read(proj)


async def list_projects(user: User, db: AsyncSession) -> list[ProjectRead]:
    result = await db.execute(
        select(Project).where(Project.user_id == user.id).order_by(Project.created_at.desc())
    )
    return [_to_read(p) for p in result.scalars().all()]


async def get_project(project_id: uuid.UUID, user: User, db: AsyncSession) -> ProjectRead:
    proj = await _get_or_404(project_id, user, db)
    return _to_read(proj)


async def update_project(project_id: uuid.UUID, data: ProjectUpdate, user: User, db: AsyncSession) -> ProjectRead:
    proj = await _get_or_404(project_id, user, db)
    if data.name is not None:        proj.name = data.name.strip()
    if data.description is not None: proj.description = data.description
    if data.status is not None:      proj.status = data.status
    await db.flush()
    await db.refresh(proj)
    return _to_read(proj)


async def delete_project(project_id: uuid.UUID, user: User, db: AsyncSession) -> None:
    proj = await _get_or_404(project_id, user, db)
    await db.delete(proj)


async def _get_or_404(project_id: uuid.UUID, user: User, db: AsyncSession) -> Project:
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == user.id)
    )
    proj = result.scalar_one_or_none()
    if not proj:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    return proj
