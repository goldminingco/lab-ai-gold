# ⬡ LAB AI GOLD

> SaaS de análise geoespacial probabilística para prospecção de ouro.
> Upload de área KML/KMZ → 10 pontos prioritários no mapa com scores e justificativas.

---

## 🚀 Setup em 2 comandos

```bash
git clone <url> lab-ai-gold && cd lab-ai-gold
bash setup.sh
```

Ou manualmente:

```bash
# 1. Cria o .env com SECRET_KEY automática
cp apps/api/.env.example apps/api/.env
SECRET=$(openssl rand -hex 32)
sed -i "s/TROQUE_POR_UMA_CHAVE_SECRETA_FORTE_DE_64_CHARS/$SECRET/" apps/api/.env

# 2. Sobe tudo (db → migrate → seed → api → web)
cd infra && docker compose up --build
```

### Acesso após subir

| Serviço | URL |
|---------|-----|
| 🌐 Frontend | http://localhost:3000 |
| 📡 API Docs | http://localhost:8000/docs |
| ❤️ Health | http://localhost:8000/health |

### Credenciais Admin padrão

| Campo | Valor |
|-------|-------|
| E-mail | `admin@labai.gold` |
| Senha | `admin123` |

> ⚠️ Troque a senha após o primeiro login!

### KML de teste
Disponível em **http://localhost:3000/area-teste.kml** (também no menu lateral)

---

## 🗺️ Fluxo completo de uso

1. Acesse http://localhost:3000 → **Criar conta** ou login admin
2. **Novo Projeto** → dê um nome
3. **Upload KML/KMZ** (arraste ou clique) — use o `area-teste.kml` para testar
4. Clique **⚡ Analisar área**
5. Veja os **10 pontos coloridos** no mapa — clique para ver detalhes
6. Aba **📍 Pontos** → scores, barras de progresso e justificativas
7. Botão **📄 PDF** → baixa o relatório completo
8. **📊 Histórico** → todas as análises do projeto

---

## 🗂️ Estrutura

```
lab-ai-gold/
├── apps/
│   ├── api/                        # FastAPI · Python 3.11
│   │   ├── app/
│   │   │   ├── core/               # config.py · security.py · deps.py
│   │   │   ├── db/                 # session.py · base.py
│   │   │   ├── models/             # User · Project · Area · Analysis · Point
│   │   │   ├── schemas/            # Pydantic DTOs
│   │   │   ├── routes/             # auth · projects · reports · admin
│   │   │   └── services/
│   │   │       ├── auth_service.py
│   │   │       ├── kml_parser.py       # parser server-side KML/KMZ
│   │   │       ├── area_service.py
│   │   │       ├── analysis_engine.py  # orquestrador
│   │   │       ├── analysis_engine_v1.py  # scoring multi-fator
│   │   │       └── report_service.py   # gerador PDF
│   │   ├── alembic/versions/001_initial.py
│   │   └── seed.py
│   │
│   └── web/                        # Next.js 14 · TypeScript · Tailwind
│       └── src/
│           ├── app/
│           │   ├── page.tsx                    # Landing page
│           │   ├── auth/login · register
│           │   └── dashboard/
│           │       ├── page.tsx                # Painel com stats
│           │       ├── projects/page.tsx        # Lista de projetos
│           │       ├── projects/[id]/page.tsx   # Mapa + análise
│           │       ├── projects/[id]/history/   # Histórico
│           │       └── admin/page.tsx           # Painel admin
│           ├── components/map/AnalysisMap.tsx   # MapLibre GL
│           ├── contexts/AuthContext.tsx
│           └── lib/api.ts
│
└── infra/
    ├── docker-compose.yml   # db → migrate → seed → api → web
    └── init.sql
```

---

## 📡 API Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/v1/auth/register` | Cadastro |
| POST | `/api/v1/auth/login` | Login → JWT |
| GET  | `/api/v1/auth/me` | Usuário autenticado |
| POST | `/api/v1/projects` | Criar projeto |
| GET  | `/api/v1/projects` | Listar projetos |
| GET  | `/api/v1/projects/{id}` | Detalhes do projeto |
| POST | `/api/v1/projects/{id}/area/upload` | Upload KML/KMZ |
| GET  | `/api/v1/projects/{id}/area` | Área parseada |
| POST | `/api/v1/projects/{id}/analyses` | Rodar análise |
| GET  | `/api/v1/projects/{id}/analyses` | Histórico |
| GET  | `/api/v1/projects/{id}/analyses/latest` | Última análise |
| GET  | `/api/v1/projects/{id}/analyses/{aid}/report` | Download PDF |
| GET  | `/api/v1/admin/users` | 🔒 Admin: listar usuários |
| PATCH | `/api/v1/admin/users/{id}/role` | 🔒 Admin: trocar role |
| PATCH | `/api/v1/admin/users/{id}/status` | 🔒 Admin: ativar/desativar |

---

## 🧠 Engine de Análise (v1)

O algoritmo pondera **5 fatores geoespaciais**:

| Fator | Peso | Fonte (v2+) |
|-------|------|-------------|
| Anomalia de ferro | 30% | Landsat SWIR bandas 5/6 |
| Gradiente de relevo | 25% | SRTM DEM 30m |
| Densidade de drenagem | 20% | OpenStreetMap Hydro |
| NDVI (vegetação) | 15% | Sentinel-2 B4/B8 |
| Temperatura superficial | 10% | MODIS LST |

Distribuição garantida: **3 alta · 4 média · 3 baixa prioridade**

---

## 🛠️ Comandos úteis

```bash
# Logs
docker compose logs -f api
docker compose logs -f web

# Recriar banco do zero
docker compose down -v && docker compose up --build

# Migração manual
docker compose exec api alembic upgrade head

# Seed manual
docker compose exec api python seed.py
```

---

## 📍 Roadmap

| Sprint | Status | Conteúdo |
|--------|--------|----------|
| 0 | ✅ | Scaffold, Docker, Postgres+PostGIS |
| 1 | ✅ | Auth JWT + RBAC + CRUD projetos |
| 2 | ✅ | Upload KML/KMZ + mapa MapLibre |
| 3 | ✅ | Engine v0 (10 pontos 3/4/3) |
| 4 | ✅ | Engine v1 (5 fatores ponderados) |
| 5 | ✅ | Relatório PDF + histórico |
| 6 | ✅ | Painel admin (roles, status) |
| 7 | 🔜 | Fase 2 premium · worker Redis · rasters reais |

---

> ⚠️ **Aviso legal:** Resultados são estimativas probabilísticas. Não garantem presença de ouro. Consulte um geólogo licenciado.
