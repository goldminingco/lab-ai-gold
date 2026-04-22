#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "⬡ LAB AI GOLD — Setup"
echo "━━━━━━━━━━━━━━━━━━━━━"

if [ ! -f apps/api/.env ]; then
  cp apps/api/.env.example apps/api/.env
  SECRET=$(openssl rand -hex 32)
  sed -i "s/TROQUE_POR_UMA_CHAVE_SECRETA_FORTE_DE_64_CHARS/$SECRET/" apps/api/.env
  echo "✅ .env criado com SECRET_KEY gerado automaticamente"
else
  echo "ℹ️  .env já existe — pulando"
fi

echo ""
echo "🚀 Subindo containers..."
cd infra
docker compose up --build -d

echo ""
echo "⏳ Aguardando serviços (30s)..."
sleep 30

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━"
echo "✅ LAB AI GOLD rodando!"
echo ""
echo "  🌐 Frontend  →  http://localhost:3000"
echo "  📡 API Docs  →  http://localhost:8000/docs"
echo "  ❤️  Health   →  http://localhost:8000/health"
echo ""
echo "  📎 KML teste → http://localhost:3000/area-teste.kml"
echo "━━━━━━━━━━━━━━━━━━━━━"
