"""
LAB AI GOLD — API Principal
FastAPI com CORS, security headers, health check e roteamento versionado.
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import ORJSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.db.session import engine


# Sao Lifecycle ----------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup e shutdown da aplicacao."""
        print(f"[startup] {settings.APP_NAME} v{settings.APP_VERSION} iniciando...")
    print(f"  Ambiente : {settings.ENVIRONMENT}")
    print(f"  DB URL   : {settings.DATABASE_URL[:40]}...")
    yield
    await engine.dispose()
    print("[shutdown] API encerrada.")


# Sao App ---------------------------------------------------------------------
_is_prod = settings.ENVIRONMENT.lower() == "production"

app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
                    "API de analise geoespacial probabilistica para prospeccao de ouro. "
                    "Os resultados sao estimativas baseadas em dados disponiveis e NAO "
                    "garantem a presenca de ouro."
        ),
        default_response_class=ORJSONResponse,
        docs_url=None if _is_prod and not settings.DEBUG else "/docs",
    redoc_url=None if _is_prod and not settings.DEBUG else "/redoc",
        openapi_url=None if _is_prod and not settings.DEBUG else "/openapi.json",
    lifespan=lifespan,
)


# Sao Security Headers Middleware ---------------------------------------------
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
                response = await call_next(request)
                response.headers.setdefault("X-Content-Type-Options", "nosniff")
                response.headers.setdefault("X-Frame-Options", "DENY")
                response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
                response.headers.setdefault(
            "Permissions-Policy",
                    "camera=(), microphone=(), geolocation=(), interest-cohort=()",
                )
                if _is_prod:
                                response.headers.setdefault(
                                                    "Strict-Transport-Security",
                                                    "max-age=63072000; includeSubDomains; preload",
                                )
                            response.headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
        response.headers.setdefault("X-XSS-Protection", "0")
        return response


app.add_middleware(SecurityHeadersMiddleware)

                                    # Sao Trusted Hosts ------------------------------------------------------------
allowed_hosts = getattr(settings, "ALLOWED_HOSTS", None) or ["*"]
if _is_prod and allowed_hosts != ["*"]:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)

# Sao CORS ---------------------------------------------------------------------
app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"],
        max_age=600,
)


# Sao Rotas base ---------------------------------------------------------------
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
                    "message": f"Bem-vindo a {settings.APP_NAME} API",
                    "docs": "/docs" if not _is_prod else "disabled",
                    "health": "/health",
}


# Sao Routers ------------------------------------------------------------------
from app.routes import auth, projects  # noqa: E402

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["Projects"])

from app.routes.reports import router as reports_router, admin_router  # noqa

app.include_router(reports_router, prefix="/api/v1", tags=["Reports"])
app.include_router(admin_router, prefix="/api/v1/admin", tags=["Admin"])
