from __future__ import annotations
import uuid
from datetime import datetime
from sqlalchemy import String, Enum as SAEnum, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
import enum

class UserRole(str, enum.Enum):
    user      = "user"
    geologist = "geologist"
    admin     = "admin"

class UserStatus(str, enum.Enum):
    active   = "active"
    inactive = "inactive"
    pending  = "pending"

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str]     = mapped_column(String(120), nullable=False)
    email: Mapped[str]    = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole]     = mapped_column(SAEnum(UserRole), default=UserRole.user, nullable=False)
    status: Mapped[UserStatus] = mapped_column(SAEnum(UserStatus), default=UserStatus.active, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    projects: Mapped[list["Project"]] = relationship("Project", back_populates="owner", lazy="selectin")  # noqa

    def __repr__(self) -> str:
        return f"<User {self.email} [{self.role}]>"
