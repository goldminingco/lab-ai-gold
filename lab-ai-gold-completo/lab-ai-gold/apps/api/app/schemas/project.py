from __future__ import annotations
import uuid
from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict
from app.models.project import ProjectStatus, ProjectPhase
from app.models.area_analysis import ParseStatus, AnalysisStatus, Priority


# ─── Project ──────────────────────────────────────────────────────────────────
class ProjectCreate(BaseModel):
    name:        str
    description: str | None = None

class ProjectUpdate(BaseModel):
    name:        str | None = None
    description: str | None = None
    status:      ProjectStatus | None = None

class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id:          uuid.UUID
    user_id:     uuid.UUID
    name:        str
    description: str | None
    status:      ProjectStatus
    phase:       ProjectPhase
    created_at:  datetime
    has_area:    bool = False
    has_analysis: bool = False


# ─── Project Area ─────────────────────────────────────────────────────────────
class AreaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id:                uuid.UUID
    project_id:        uuid.UUID
    original_filename: str
    geojson:           dict | None
    area_ha:           float | None
    centroid_lat:      float | None
    centroid_lng:      float | None
    bounds_json:       dict | None
    parse_status:      ParseStatus
    parse_error:       str | None
    created_at:        datetime


# ─── Analysis ─────────────────────────────────────────────────────────────────
class AnalysisPointRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id:           uuid.UUID
    label:        str
    lat:          float
    lng:          float
    score:        float
    priority:     Priority
    color:        str
    rank:         int
    reasons_json: list[str]

class AnalysisRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id:                uuid.UUID
    project_id:        uuid.UUID
    phase:             str
    status:            AnalysisStatus
    algorithm_version: str
    summary_json:      dict | None
    started_at:        datetime | None
    finished_at:       datetime | None
    created_at:        datetime
    points:            list[AnalysisPointRead] = []
