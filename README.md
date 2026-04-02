# Threadline

A full-stack social feed platform.
Users can register, log in, create posts with text and images, like and unlike posts/comments/replies, comment, reply, and control who sees their content with public/private visibility. The UI is a pixel-perfect conversion of three provided static HTML/CSS files into a production-ready React application.

---

## Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14 (App Router, TypeScript) |
| Backend | FastAPI (Python 3.12) |
| Database | PostgreSQL 16 |
| Auth | JWT — httpOnly cookies (15m access + 7d refresh) |
| ORM | SQLModel + Alembic (async SQLAlchemy) |
| Data fetching | TanStack React Query |
| HTTP client | Axios with silent refresh interceptor |
| Container | Docker + Docker Compose |

---

## Running the Project

There are two ways to run Threadline — with Docker (recommended, zero setup) or locally (requires PostgreSQL, Python 3.12+, and Node 20+).

---

### Option A — Docker (recommended)

**Prerequisites:** [Docker](https://docs.docker.com/get-docker/) + [Docker Compose v2](https://docs.docker.com/compose/install/)

```bash
git clone https://github.com/Motssembillahmahin/threadline.git
cd threadline
make setup          # creates .env from .env.example
```

Open `.env` and fill in your secrets:

```env
DB_PASSWORD=your_postgres_password
ACCESS_SECRET=your_access_token_secret_min_32_chars
REFRESH_SECRET=your_refresh_token_secret_min_32_chars
```

```bash
make up             # builds images, starts containers, runs migrations
```

First run takes ~2–3 minutes. Done.

---

### Option B — Local (without Docker)

**Prerequisites:** PostgreSQL 16, Python 3.12+, Node 20+

```bash
git clone https://github.com/Motssembillahmahin/threadline.git
cd threadline
make local-setup    # creates venv, installs deps, copies env files
```

Edit `backend/.env` — set your local PostgreSQL connection and secrets:

```env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/threadline
ACCESS_SECRET=your_access_token_secret_min_32_chars
REFRESH_SECRET=your_refresh_token_secret_min_32_chars
UPLOAD_DIR=app/static/uploads
CORS_ORIGINS=http://localhost:3000
```

Create the database, run migrations, then start both servers (two terminals):

```bash
# Terminal 1
createdb threadline      # or: psql -U postgres -c "CREATE DATABASE threadline"
make local-migrate       # runs alembic upgrade head

# Terminal 2
make local-backend       # FastAPI on http://localhost:8000

# Terminal 3
make local-frontend      # Next.js on http://localhost:3000
```

---

### Services

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |

---

## Make Commands

**Docker**
```
make setup           Copy .env.example → .env
make up              Build images and start all services (detached)
make down            Stop and remove containers
make restart         Restart all services
make build           Rebuild images without cache
make logs            Tail logs for all services
make logs-backend    Tail backend logs only
make logs-frontend   Tail frontend logs only
make migrate         Run Alembic migrations (upgrade head)
make migrate-down    Rollback last Alembic migration
make db-shell        Open psql shell in the db container
make backend-shell   Open bash shell in the backend container
make frontend-shell  Open sh shell in the frontend container
make clean           Remove containers, images, and volumes (destructive)
```

**Local**
```
make local-setup     Install Python venv + npm deps + copy env files
make local-migrate   Run Alembic migrations against local PostgreSQL
make local-backend   Start FastAPI dev server on :8000
make local-frontend  Start Next.js dev server on :3000
```

---

## Features

### Implemented
- Register and login with email/password
- JWT authentication via httpOnly cookies — no tokens in localStorage
- Silent token refresh via Axios interceptor — users never see a session expiry
- Create posts with text and/or image upload
- Public/private post visibility — private posts visible only to the author
- Cursor-based feed pagination — performant at any scale
- Like and unlike posts, comments, and replies with optimistic UI updates
- "Who liked this" modal — click any like count to see the full list
- Comments and nested replies
- Delete own posts
- Dark mode toggle (preserves original custom.js behaviour)
- Fully responsive layout matching the original static HTML design

### Static UI only (as per task scope)
- Stories carousel
- Left sidebar: Explore menu, Suggested People
- Right sidebar: You Might Like, Your Friends
- Notifications dropdown
- Google OAuth button (non-functional)

---

## Project Structure

```
threadline/
├── Makefile
├── docker-compose.yml
├── .env.example
├── docs/                    # Project documentation
│   ├── index.md
│   ├── architecture.md
│   ├── scalability.md
│   ├── frontend-workflow.md
│   └── html-to-nextjs.md
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic/
│   └── app/
│       ├── main.py
│       ├── config.py
│       ├── database.py
│       ├── models/
│       ├── schemas/
│       ├── routers/
│       ├── services/
│       └── middleware/
└── frontend/
    ├── Dockerfile
    ├── next.config.ts
    ├── src/
    │   ├── app/
    │   ├── components/
    │   ├── context/
    │   ├── hooks/
    │   ├── lib/
    │   └── types/
    └── public/assets/       # Original CSS, images, fonts (unchanged)
```

---

## Design Decisions

Cursor pagination over OFFSET, denormalized counters, httpOnly cookies over localStorage, and pixel-perfect HTML/CSS preservation — see [docs/](./docs/index.md) for the full rationale.

---

## Documentation

| Document | Description |
|---|---|
| [Architecture](./docs/architecture.md) | System design, DB schema, API reference, auth flow |
| [Scalability](./docs/scalability.md) | How the system handles millions of posts |
| [Frontend Workflow](./docs/frontend-workflow.md) | Auth flow, React Query, optimistic updates |
| [HTML to Next.js](./docs/html-to-nextjs.md) | How the static design was converted to Next.js |

---

## Development Notes

**Docker — reset to clean state:**
```bash
make clean    # removes containers and volumes (data is lost)
make up       # fresh start, migrations run automatically
```

**Local — reset database:**
```bash
dropdb threadline && createdb threadline
make local-migrate
```

**Inspect the database (Docker):**
```bash
make db-shell
# inside psql:
\dt
SELECT id, content, like_count FROM posts ORDER BY created_at DESC LIMIT 5;
```

**Inspect the database (local):**
```bash
psql -U postgres -d threadline
```
