from __future__ import annotations
import uuid
from datetime import datetime
from sqlalchemy import String, Text, ForeignKey, Enum as SAEnum, DateTime, func, Float, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
import enum

class ParseStatus(str, enum.Enum):
    pending = "pending"
    ok      = "ok"
    error   = "error"

class AnalysisStatus(str, enum.Enum):
    pending  = "pending"
    running  = "running"
    done     = "done"
    error    = "error"

class Priority(str, enum.Enum):
    high   = "high"
    medium = "medium"
    low    = "low"


class ProjectArea(Base):
    __tablename__ = "project_areas"

    id: Mapped[uuid.UUID]         = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    original_filename: Mapped[str]       = mapped_column(String(255))
    storage_path: Mapped[str]            = mapped_column(String(512))
    geojson: Mapped[dict | None]         = mapped_column(JSONB, nullable=True)
    area_ha: Mapped[float | None]        = mapped_column(Float, nullable=True)
    centroid_lat: Mapped[float | None]   = mapped_column(Float, nullable=True)
    centroid_lng: Mapped[float | None]   = mapped_column(Float, nullable=True)
    bounds_json: Mapped[dict | None]     = mapped_column(JSONB, nullable=True)
    parse_status: Mapped[ParseStatus]    = mapped_column(SAEnum(ParseStatus), default=ParseStatus.pending)
    parse_error: Mapped[str | None]      = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime]         = mapped_column(DateTime(timezone=True), server_default=func.now())

    project: Mapped["Project"] = relationship("Project", back_populates="areas")  # noqa


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[uuid.UUID]           = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID]   = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    requested_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    phase: Mapped[str]              = mapped_column(String(20), default="phase1")
    status: Mapped[AnalysisStatus]  = mapped_column(SAEnum(AnalysisStatus), default=AnalysisStatus.pending)
    algorithm_version: Mapped[str]  = mapped_column(String(20), default="v0")
    summary_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    started_at: Mapped[datetime | None]  = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime]         = mapped_column(DateTime(timezone=True), server_default=func.now())

    project: Mapped["Project"]           = relationship("Project", back_populates="analyses")  # noqa
    points:  Mapped[list["AnalysisPoint"]] = relationship("AnalysisPoint", back_populates="analysis", lazy="selectin")  # noqa


class AnalysisPoint(Base):
    __tablename__ = "analysis_points"

    id: Mapped[uuid.UUID]           = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id: Mapped[uuid.UUID]  = mapped_column(UUID(as_uuid=True), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    label: Mapped[str]              = mapped_column(String(50))
    lat: Mapped[float]              = mapped_column(Float)
    lng: Mapped[float]              = mapped_column(Float)
    score: Mapped[float]            = mapped_column(Float)
    priority: Mapped[Priority]      = mapped_column(SAEnum(Priority))
    color: Mapped[str]              = mapped_column(String(10))   # "#ef4444"
    rank: Mapped[int]               = mapped_column(Integer)
    reasons_json: Mapped[list]      = mapped_column(JSONB, default=list)

    analysis: Mapped["Analysis"] = relationship("Analysis", back_populates="points")  # noqa
