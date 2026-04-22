"""
Sessão assíncrona do SQLAlchemy.
Exporta: engine, AsyncSessionLocal, get_db (dependency FastAPI).
"""
from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

# ─── Engine ───────────────────────────────────────────────────────────────────
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,           # loga SQL em desenvolvimento
    pool_pre_ping=True,            # verifica conexão antes de usar
    pool_size=10,
    max_overflow=20,
)

# ─── Session factory ──────────────────────────────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,        # evita lazy loading pós-commit
    autoflush=False,
)


# ─── Dependency FastAPI ───────────────────────────────────────────────────────
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency que fornece uma sessão de banco por request.
    Garante rollback em caso de erro e fechamento sempre.

    Uso:
        @router.get("/")
        async def handler(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
