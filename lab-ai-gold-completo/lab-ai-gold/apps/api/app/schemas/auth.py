from __future__ import annotations
import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from app.models.user import UserRole, UserStatus


class UserCreate(BaseModel):
    name:     str
    email:    EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Senha deve ter pelo menos 6 caracteres")
        return v

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Nome não pode ser vazio")
        return v.strip()


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id:         uuid.UUID
    name:       str
    email:      str
    role:       UserRole
    status:     UserStatus
    created_at: datetime


class LoginRequest(BaseModel):
    email:    EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token:  str
    refresh_token: str
    token_type:    str = "bearer"
    user:          UserRead
