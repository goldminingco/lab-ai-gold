from __future__ import annotations
import os
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.area_analysis import ParseStatus, ProjectArea
from app.models.project import Project
from app.models.user import User
from app.schemas.project import AreaRead
from app.services.kml_parser import parse_kml_bytes

ALLOWED_EXT = {".kml", ".kmz"}


async def upload_area(
    project_id: uuid.UUID,
    file: UploadFile,
    user: User,
    db: AsyncSession,
) -> AreaRead:
    # Verifica se projeto pertence ao usuário
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == user.id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")

    # Valida extensão
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXT:
        raise HTTPException(status_code=400, detail="Apenas arquivos .kml e .kmz são aceitos")

    content = await file.read()
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail=f"Arquivo muito grande (máx {settings.MAX_UPLOAD_SIZE_MB}MB)")

    # Salva no storage local
    upload_dir = Path(settings.UPLOAD_DIR) / str(project_id)
    upload_dir.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid.uuid4()}{suffix}"
    storage_path = upload_dir / stored_name
    storage_path.write_bytes(content)

    # Cria registro com status pending
    area = ProjectArea(
        project_id=project_id,
        original_filename=file.filename or stored_name,
        storage_path=str(storage_path),
        parse_status=ParseStatus.pending,
    )
    db.add(area)
    await db.flush()

    # Parse síncrono (Sprint 5 moverá para worker)
    try:
        parsed = parse_kml_bytes(content, file.filename or "")
        area.geojson      = parsed["geojson"]
        area.area_ha      = parsed["area_ha"]
        area.centroid_lat = parsed["centroid_lat"]
        area.centroid_lng = parsed["centroid_lng"]
        area.bounds_json  = parsed["bounds_json"]
        area.parse_status = ParseStatus.ok
    except ValueError as e:
        area.parse_status = ParseStatus.error
        area.parse_error  = str(e)

    await db.flush()
    await db.refresh(area)
    return AreaRead.model_validate(area)
