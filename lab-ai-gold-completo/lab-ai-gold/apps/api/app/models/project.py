from __future__ import annotations
import uuid
from datetime import datetime
from sqlalchemy import String, Text, ForeignKey, Enum as SAEnum, DateTime, func, Float, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
import enum

class ProjectStatus(str, enum.Enum):
    active   = "active"
    archived = "archived"

class ProjectPhase(str, enum.Enum):
    phase1 = "phase1"
    phase2 = "phase2"

class Project(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID]      = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str]          = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ProjectStatus]   = mapped_column(SAEnum(ProjectStatus), default=ProjectStatus.active)
    phase: Mapped[ProjectPhase]     = mapped_column(SAEnum(ProjectPhase), default=ProjectPhase.phase1)
    created_at: Mapped[datetime]    = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime]    = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    owner:    Mapped["User"]            = relationship("User", back_populates="projects")  # noqa
    areas:    Mapped[list["ProjectArea"]] = relationship("ProjectArea", back_populates="project", lazy="selectin")  # noqa
    analyses: Mapped[list["Analysis"]]   = relationship("Analysis",     back_populates="project", lazy="selectin")  # noqa
