from __future__ import annotations
import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.area_analysis import Analysis, AnalysisPoint, ProjectArea
from app.models.project import Project
from app.models.user import User, UserRole
from app.schemas.auth import UserRead
from app.services.report_service import generate_report_pdf

router = APIRouter()


@router.get(
    "/projects/{project_id}/analyses/{analysis_id}/report",
    tags=["Reports"],
    summary="Download relatório PDF",
)
async def download_report(
    project_id:  uuid.UUID,
    analysis_id: uuid.UUID,
    db:   AsyncSession = Depends(get_db),
    user: User         = Depends(get_current_user),
):
    # Carrega projeto
    proj_res = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == user.id)
    )
    project = proj_res.scalar_one_or_none()
    if not project:
        from fastapi import HTTPException
        raise HTTPException(404, "Projeto não encontrado")

    # Carrega análise
    an_res = await db.execute(
        select(Analysis).where(Analysis.id == analysis_id, Analysis.project_id == project_id)
    )
    analysis = an_res.scalar_one_or_none()
    if not analysis:
        from fastapi import HTTPException
        raise HTTPException(404, "Análise não encontrada")

    # Pontos
    pts_res = await db.execute(
        select(AnalysisPoint).where(AnalysisPoint.analysis_id == analysis_id)
        .order_by(AnalysisPoint.rank)
    )
    pts = pts_res.scalars().all()

    # Área
    area_res = await db.execute(
        select(ProjectArea).where(ProjectArea.project_id == project_id,
                                  ProjectArea.parse_status == "ok")
        .order_by(ProjectArea.created_at.desc())
    )
    area = area_res.scalars().first()

    pts_dicts = [
        {
            "label":        p.label,
            "lat":          p.lat,
            "lng":          p.lng,
            "score":        p.score,
            "priority":     p.priority.value,
            "color":        p.color,
            "rank":         p.rank,
            "reasons_json": p.reasons_json,
        }
        for p in pts
    ]

    pdf_bytes = generate_report_pdf(
        project_name=project.name,
        project_description=project.description,
        area_ha=area.area_ha if area else None,
        analysis=analysis.summary_json or {},
        points=pts_dicts,
        user_name=user.name,
    )

    filename = f"labai-gold-{project.name.lower().replace(' ', '-')}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ─── Admin ────────────────────────────────────────────────────────────────────
admin_router = APIRouter()


@admin_router.get("/users", response_model=list[UserRead], summary="Listar todos os usuários")
async def list_all_users(
    db:   AsyncSession         = Depends(get_db),
    user: User                 = Depends(require_role(UserRole.admin)),
):
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    return [UserRead.model_validate(u) for u in result.scalars().all()]


@admin_router.patch("/users/{user_id}/role", response_model=UserRead, summary="Alterar role do usuário")
async def set_user_role(
    user_id: uuid.UUID,
    role:    UserRole,
    db:      AsyncSession = Depends(get_db),
    _admin:  User         = Depends(require_role(UserRole.admin)),
):
    result = await db.execute(select(User).where(User.id == user_id))
    target = result.scalar_one_or_none()
    if not target:
        from fastapi import HTTPException
        raise HTTPException(404, "Usuário não encontrado")
    target.role = role
    await db.flush()
    await db.refresh(target)
    return UserRead.model_validate(target)


@admin_router.patch("/users/{user_id}/status", response_model=UserRead, summary="Ativar/desativar usuário")
async def set_user_status(
    user_id: uuid.UUID,
    status:  str,
    db:      AsyncSession = Depends(get_db),
    _admin:  User         = Depends(require_role(UserRole.admin)),
):
    from app.models.user import UserStatus
    result = await db.execute(select(User).where(User.id == user_id))
    target = result.scalar_one_or_none()
    if not target:
        from fastapi import HTTPException
        raise HTTPException(404, "Usuário não encontrado")
    try:
        target.status = UserStatus(status)
    except ValueError:
        from fastapi import HTTPException
        raise HTTPException(400, f"Status inválido: {status}")
    await db.flush()
    await db.refresh(target)
    return UserRead.model_validate(target)
