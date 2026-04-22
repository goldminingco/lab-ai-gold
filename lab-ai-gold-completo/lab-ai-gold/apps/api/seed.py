#!/usr/bin/env python3
"""
Seed script — cria usuário admin padrão se não existir.
Uso: python seed.py
Requer DATABASE_SYNC_URL no .env ou como variável de ambiente.
"""
import os
import sys
from pathlib import Path

# Garante que o módulo app está no path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from app.models.user import User, UserRole, UserStatus
from app.core.security import hash_password
from app.db.base import Base
import uuid

SYNC_URL = os.environ.get("DATABASE_SYNC_URL") or os.environ.get(
    "DATABASE_URL", ""
).replace("postgresql+asyncpg://", "postgresql+psycopg2://")

if not SYNC_URL:
    print("❌ DATABASE_SYNC_URL não definida")
    sys.exit(1)

engine = create_engine(SYNC_URL, echo=False)

ADMIN_NAME     = os.environ.get("SEED_ADMIN_NAME",     "Admin LAB AI")
ADMIN_EMAIL    = os.environ.get("SEED_ADMIN_EMAIL",    "admin@labai.gold")
ADMIN_PASSWORD = os.environ.get("SEED_ADMIN_PASSWORD", "admin123")

with Session(engine) as session:
    existing = session.execute(select(User).where(User.email == ADMIN_EMAIL)).scalar_one_or_none()
    if existing:
        print(f"ℹ️  Admin já existe: {ADMIN_EMAIL}")
    else:
        admin = User(
            id=uuid.uuid4(),
            name=ADMIN_NAME,
            email=ADMIN_EMAIL,
            password_hash=hash_password(ADMIN_PASSWORD),
            role=UserRole.admin,
            status=UserStatus.active,
        )
        session.add(admin)
        session.commit()
        print(f"✅ Admin criado!")
        print(f"   E-mail : {ADMIN_EMAIL}")
        print(f"   Senha  : {ADMIN_PASSWORD}")
        print(f"   ⚠️  Troque a senha após o primeiro login!")
