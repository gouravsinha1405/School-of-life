# Lebensschule (MVP)

Stateful journaling + AI analysis system built with:
- Backend: FastAPI + SQLAlchemy 2 + Alembic + Postgres
- LLM: Groq via LangChain `ChatGroq` (model `gpt-oss-120b`)
- Frontend: Next.js 14 (App Router) + TypeScript + Tailwind + recharts
- Auth: email/password + JWT (also stored in an httpOnly cookie for the UI)

## Quickstart (Docker)

1) Create env files

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

2) Start services

```bash
docker compose up --build
```

3) Run migrations

```bash
docker compose exec backend alembic upgrade head
```

4) Open
- Frontend: http://localhost:3000
- Backend OpenAPI: http://localhost:8000/docs

## Project structure

```
.
├── backend/
│   ├── app/
│   ├── alembic.ini
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── package.json
│   └── Dockerfile
└── docker-compose.yml
```

## Notes
- Set `GROQ_API_KEY` in `backend/.env`.
- If the LLM returns invalid JSON, the backend retries with a JSON-fix prompt and falls back to safe defaults.

## Auth / default credentials

There are **no default login credentials**. Create users via the Register page or the API:

```bash
curl -sS -X POST http://localhost:8000/api/auth/register \
	-H 'content-type: application/json' \
	-d '{"email":"you@example.com","password":"Password123!","preferred_language":"de"}'
```

## Load / concurrency testing

This repo includes a small script that can create many users and post entries concurrently.

```bash
python3 tools/load_test.py --users 200 --concurrency 40 --entries-per-user 3 --fetch-report --verbose
```

Optional (more expensive/noisy): poll analysis completion per entry:

```bash
python3 tools/load_test.py --users 50 --concurrency 10 --entries-per-user 2 --poll-analysis --poll-timeout-s 60
```
