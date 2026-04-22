"""
Helpers de segurança: hash de senha (bcrypt) e tokens JWT.
Módulo puro — sem dependências de FastAPI ou banco.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# ─── Bcrypt ───────────────────────────────────────────────────────────────────
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """Retorna o hash bcrypt da senha em texto plano."""
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Verifica se a senha em texto plano corresponde ao hash."""
    return _pwd_context.verify(plain, hashed)


# ─── JWT ──────────────────────────────────────────────────────────────────────
def _now_utc() -> datetime:
    return datetime.now(tz=timezone.utc)


def create_access_token(
    subject: str | int,
    extra_claims: Optional[dict[str, Any]] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Gera um JWT de acesso.

    Args:
        subject:      Identificador do usuário (geralmente user.id ou user.email).
        extra_claims: Claims adicionais (ex.: {"role": "admin"}).
        expires_delta: Duração customizada; padrão = ACCESS_TOKEN_EXPIRE_MINUTES.

    Returns:
        Token JWT assinado.
    """
    expire = _now_utc() + (
        expires_delta
        or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload: dict[str, Any] = {
        "sub": str(subject),
        "iat": _now_utc(),
        "exp": expire,
        "type": "access",
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(subject: str | int) -> str:
    """Gera um JWT de refresh com expiração longa."""
    expire = _now_utc() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload: dict[str, Any] = {
        "sub": str(subject),
        "iat": _now_utc(),
        "exp": expire,
        "type": "refresh",
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    """
    Decodifica e valida um JWT.

    Raises:
        JWTError: Se o token for inválido ou expirado.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


def get_subject_from_token(token: str) -> Optional[str]:
    """
    Extrai o 'sub' do token sem lançar exceção.
    Retorna None se o token for inválido.
    """
    try:
        payload = decode_token(token)
        return payload.get("sub")
    except JWTError:
        return None
