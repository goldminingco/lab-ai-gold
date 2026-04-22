"""
Orquestrador do engine de análise.
Delega para v1. Interface fixa — Regra de Ouro #5.
"""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.area_analysis import Analysis, AnalysisPoint, AnalysisStatus, Priority, ProjectArea
from app.models.project import Project
from app.models.user import User
from app.schemas.project import AnalysisRead
from app.services.analysis_engine_v1 import generate_points_v1


async def run_analysis(
    project_id: uuid.UUID,
    user: User,
    db: AsyncSession,
    algorithm_version: str = "v1",
) -> AnalysisRead:
    proj_result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == user.id)
    )
    project = proj_result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")

    area_result = await db.execute(
        select(ProjectArea)
        .where(ProjectArea.project_id == project_id, ProjectArea.parse_status == "ok")
        .order_by(ProjectArea.created_at.desc())
    )
    area = area_result.scalars().first()
    if not area or not area.bounds_json:
        raise HTTPException(status_code=400, detail="Área não enviada ou com erro no parse")

    analysis = Analysis(
        project_id=project_id,
        requested_by=user.id,
        phase="phase1",
        status=AnalysisStatus.running,
        algorithm_version=algorithm_version,
        started_at=datetime.now(tz=timezone.utc),
    )
    db.add(analysis)
    await db.flush()

    try:
        seed = int(str(project_id).replace("-", ""), 16) % (2**31)
        pts  = generate_points_v1(area.bounds_json, area.area_ha or 1000.0, seed=seed)

        for pt in pts:
            db.add(AnalysisPoint(
                analysis_id  = analysis.id,
                label        = pt.label,
                lat          = pt.lat,
                lng          = pt.lng,
                score        = pt.score,
                priority     = Priority(pt.priority),
                color        = pt.color,
                rank         = pt.rank,
                reasons_json = pt.reasons,
            ))

        analysis.status       = AnalysisStatus.done
        analysis.finished_at  = datetime.now(tz=timezone.utc)
        analysis.summary_json = {
            "total_points": 10,
            "high":   sum(1 for p in pts if p.priority == "high"),
            "medium": sum(1 for p in pts if p.priority == "medium"),
            "low":    sum(1 for p in pts if p.priority == "low"),
            "top_score": max(p.score for p in pts),
            "avg_score": round(sum(p.score for p in pts) / len(pts), 4),
            "area_ha": area.area_ha,
            "algorithm": algorithm_version,
            "factors_used": ["ferro", "relevo", "drenagem", "ndvi", "temperatura"],
            "disclaimer": (
                "Resultados probabilísticos. Não garantem presença de ouro. "
                "Consulte um geólogo licenciado."
            ),
        }

    except Exception as exc:
        analysis.status = AnalysisStatus.error
        analysis.finished_at = datetime.now(tz=timezone.utc)
        analysis.summary_json = {"error": str(exc)}
        await db.flush()
        raise HTTPException(status_code=500, detail=f"Erro no engine: {exc}") from exc

    await db.flush()
    await db.refresh(analysis)
    return AnalysisRead.model_validate(analysis)
