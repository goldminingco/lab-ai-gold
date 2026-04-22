"""
LAB AI GOLD — API Principal
FastAPI com CORS, health check e roteamento versionado.
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from app.core.config import settings
from app.db.session import engine


# ─── Lifecycle ────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup e shutdown da aplicação."""
    # Sprint 0: apenas log de inicio
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} iniciando...")
    print(f"   Ambiente : {settings.ENVIRONMENT}")
    print(f"   DB URL   : {settings.DATABASE_URL[:40]}...")
    yield
    # Shutdown
    await engine.dispose()
    print("👋 API encerrada.")


# ─── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "API de análise geoespacial probabilística para prospecção de ouro. "
        "Os resultados são estimativas baseadas em dados disponíveis e NÃO "
        "garantem a presença de ouro."
    ),
    default_response_class=ORJSONResponse,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)


# ─── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Rotas base ───────────────────────────────────────────────────────────────
@app.get("/health", tags=["System"], summary="Health check")
async def health_check():
    """Retorna status da API. Usado por Docker healthcheck e load balancer."""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/", tags=["System"], summary="Root")
async def root():
    return {
        "message": f"Bem-vindo à {settings.APP_NAME} API",
        "docs": "/docs",
        "health": "/health",
    }


# ─── Routers ──────────────────────────────────────────────────────────────────
from app.routes import auth, projects  # noqa: E402

app.include_router(auth.router,     prefix="/api/v1/auth",     tags=["Auth"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["Projects"])

from app.routes.reports import router as reports_router, admin_router  # noqa
app.include_router(reports_router, prefix="/api/v1", tags=["Reports"])
app.include_router(admin_router, prefix="/api/v1/admin", tags=["Admin"])
