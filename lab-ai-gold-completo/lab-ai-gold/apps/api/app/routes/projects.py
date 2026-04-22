from __future__ import annotations
import uuid

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.area_analysis import Analysis, ProjectArea
from app.models.user import User
from app.schemas.project import AnalysisRead, AreaRead, ProjectCreate, ProjectRead, ProjectUpdate
from app.services import analysis_engine, area_service, project_service

router = APIRouter()


# ─── Projetos ─────────────────────────────────────────────────────────────────
@router.post("", response_model=ProjectRead, status_code=201)
async def create_project(
    data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await project_service.create_project(data, user, db)


@router.get("", response_model=list[ProjectRead])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await project_service.list_projects(user, db)


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await project_service.get_project(project_id, user, db)


@router.patch("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: uuid.UUID,
    data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await project_service.update_project(project_id, data, user, db)


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await project_service.delete_project(project_id, user, db)


# ─── Área ─────────────────────────────────────────────────────────────────────
@router.post("/{project_id}/area/upload", response_model=AreaRead, status_code=201)
async def upload_area(
    project_id: uuid.UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await area_service.upload_area(project_id, file, user, db)


@router.get("/{project_id}/area", response_model=AreaRead | None)
async def get_area(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ProjectArea)
        .where(ProjectArea.project_id == project_id)
        .order_by(ProjectArea.created_at.desc())
    )
    area = result.scalars().first()
    if not area:
        return None
    return AreaRead.model_validate(area)


# ─── Análise ──────────────────────────────────────────────────────────────────
@router.post("/{project_id}/analyses", response_model=AnalysisRead, status_code=201)
async def run_analysis(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await analysis_engine.run_analysis(project_id, user, db)


@router.get("/{project_id}/analyses", response_model=list[AnalysisRead])
async def list_analyses(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Analysis)
        .where(Analysis.project_id == project_id)
        .order_by(Analysis.created_at.desc())
    )
    return [AnalysisRead.model_validate(a) for a in result.scalars().all()]


@router.get("/{project_id}/analyses/latest", response_model=AnalysisRead | None)
async def get_latest_analysis(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Analysis)
        .where(Analysis.project_id == project_id, Analysis.status == "done")
        .order_by(Analysis.created_at.desc())
    )
    a = result.scalars().first()
    return AnalysisRead.model_validate(a) if a else None
