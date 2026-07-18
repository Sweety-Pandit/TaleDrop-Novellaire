# TaleDrop-Novellaire

An AI-powered novel publishing platform — readers browse, bookmark, review,
and purchase premium chapters; authors publish serialized fiction chapter by
chapter; a local AI companion summarizes stories and answers questions about
them using RAG.

## Tech stack

| Layer    | Stack |
|----------|-------|
| Frontend | React 18 + Vite, TypeScript, React Router, Tailwind CSS, Zustand, Axios |
| Backend  | FastAPI, SQLAlchemy, Alembic, PostgreSQL, JWT auth |
| AI       | Ollama (local LLM), Sentence Transformers (embeddings), ChromaDB (vector store), LangGraph (orchestration) |
| Payments | Razorpay |

## Project structure

```
taledrop-novellaire/
├── backend/          FastAPI app (see backend/app/ for routers, services, models)
├── frontend/          React + Vite SPA (see frontend/src/app/ for routes)
├── ai_engine/         Local AI: embeddings, vector store, RAG, LLM calls, LangGraph agents
├── docker-compose.yml Full local stack: Postgres, Ollama, backend, frontend
└── .env.example       Env vars consumed by docker-compose.yml
```

Each of `backend/` and `frontend/` also has its own `.env.example` for running
that piece directly (outside Docker) — see "Manual setup" below.

## Quick start (Docker — recommended)

Requires Docker and Docker Compose.

```bash
cp .env.example .env          # edit if you want real email/Razorpay creds
docker compose up --build
```

This starts Postgres, Ollama, the backend (`:8000`), and the frontend
(`:3000`). First run will take a few minutes (building images, pulling
the Postgres/Ollama base images).

**Pull an LLM model for the AI features** (the Ollama image ships with no
models installed):

```bash
docker compose exec ollama ollama pull llama3.1
```

Then open **http://localhost:3000**. API docs are at
**http://localhost:8000/docs**.

To stop: `docker compose down` (add `-v` to also delete the Postgres/Ollama/
uploads/ChromaDB volumes and start fresh).

### A note on `VITE_API_BASE_URL`

Vite inlines `VITE_*` variables into the browser bundle at *build* time, not
at container start. If you change the port the backend is published on, you
must rebuild the frontend image with the new value:

```bash
docker compose build --build-arg VITE_API_BASE_URL=http://localhost:8000/api/v1 frontend
```

## Manual setup (no Docker)

Useful for active development (hot reload, debugging).

### 1. Database

Run Postgres however you like (Docker, Homebrew, native install). Create a
database matching `DATABASE_URL` in `backend/.env`.

### 2. Backend

```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # edit DATABASE_URL etc.
uvicorn app.main:app --reload   # http://localhost:8000
```

> `sentence-transformers` pulls in PyTorch, a large dependency. If you don't
> need the AI features yet, everything else in the app works fine without it
> — it's only imported lazily when `ai_engine.embeddings` is actually used.

### 3. Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev                     # http://localhost:3000
```

### 4. Ollama (for AI features)

Install from [ollama.com](https://ollama.com), then:

```bash
ollama serve
ollama pull llama3.1
```

Set `OLLAMA_BASE_URL=http://localhost:11434` and `OLLAMA_MODEL=llama3.1` in
`backend/.env` (these are already the defaults).

## Environment variables

See `backend/.env.example` and `frontend/.env.example` for the full
list with inline comments. The most important ones:

| Variable | Where | Purpose |
|----------|-------|---------|
| `DATABASE_URL` | backend | Postgres connection string |
| `JWT_SECRET_KEY` | backend | **Change this in any real deployment** |
| `RAZORPAY_KEY_ID` / `_SECRET` | backend | Payment processing |
| `MAIL_*` | backend | Email verification / password reset. Safe to leave as placeholders in local dev — failures are logged, not fatal |
| `OLLAMA_BASE_URL` / `OLLAMA_MODEL` | backend | Local LLM for AI features |
| `VITE_API_BASE_URL` | frontend | Must be reachable from the **browser** |

## What's implemented

Auth (register/login/JWT/email verification/password reset), profiles,
novel & chapter management with Markdown content, premium chapters via
Razorpay, bookmarks/library/reading history, reviews & comments, plain
database search, and three AI features: story summaries, RAG-based
Q&A grounded in a novel's chapters (with premium-content access respected),
and genre-based recommendations.

## Deliberately out of scope for this version

Per the original spec: **Character Chat, Story Continuation, AI World
Builder, and AI Translation** are planned for a future version and are not
implemented. **Semantic AI search** (as opposed to the current plain
database search) is likewise a future addition. **Jenkins CI/CD and a
production deployment configuration** have not been introduced — this
Docker setup is for local development only (`DEBUG=True`, permissive CORS,
default secrets) and should not be used as-is in production.
