from __future__ import annotations
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.models.user import User
from app.schemas.auth import UserCreate, TokenResponse, UserRead


async def register_user(data: UserCreate, db: AsyncSession) -> TokenResponse:
    result = await db.execute(select(User).where(User.email == data.email.lower()))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")

    user = User(
        name=data.name.strip(),
        email=data.email.lower(),
        password_hash=hash_password(data.password),
    )
    db.add(user)
    await db.flush()   # gera o UUID
    await db.refresh(user)

    return _build_token(user)


async def login_user(email: str, password: str, db: AsyncSession) -> TokenResponse:
    result = await db.execute(select(User).where(User.email == email.lower()))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos",
        )
    return _build_token(user)


def _build_token(user: User) -> TokenResponse:
    extra = {"role": user.role.value}
    return TokenResponse(
        access_token=create_access_token(str(user.id), extra_claims=extra),
        refresh_token=create_refresh_token(str(user.id)),
        user=UserRead.model_validate(user),
    )
