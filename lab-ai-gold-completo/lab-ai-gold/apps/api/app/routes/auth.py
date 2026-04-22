from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, UserCreate, UserRead
from app.services.auth_service import login_user, register_user

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=201, summary="Cadastro")
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    return await register_user(data, db)


@router.post("/login", response_model=TokenResponse, summary="Login")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await login_user(data.email, data.password, db)


@router.get("/me", response_model=UserRead, summary="Usuário autenticado")
async def me(user: User = Depends(get_current_user)):
    return UserRead.model_validate(user)
