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

## Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose v2](https://docs.docker.com/compose/install/)
- `make` (pre-installed on macOS/Linux; Windows: use [WSL2](https://learn.microsoft.com/en-us/windows/wsl/) or [Git Bash](https://gitforwindows.org/))

### 1. Clone and configure

```bash
git clone https://github.com/Motssembillahmahin/threadline.git
cd threadline
make setup        # creates .env from .env.example
```

Open `.env` and fill in your secrets:

```env
DB_PASSWORD=your_postgres_password
ACCESS_SECRET=your_access_token_secret_min_32_chars
REFRESH_SECRET=your_refresh_token_secret_min_32_chars
```

### 2. Build and start

```bash
make up
```

This builds all three Docker images, starts the containers, and runs Alembic migrations automatically. On first run it takes ~2–3 minutes.

### 3. Open the app

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |

---

## Make Commands

```
make setup           Copy .env.example → .env (first-time setup)
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

The backend runs migrations automatically on container start (`alembic upgrade head` before Uvicorn). This means you can reset the database volume and restart to get a clean state:

```bash
make clean    # removes volumes (data is lost)
make up       # fresh start, migrations run automatically
```

To inspect the database directly:

```bash
make db-shell
# inside psql:
\dt                        -- list tables
SELECT * FROM users;
SELECT id, content, like_count FROM posts ORDER BY created_at DESC LIMIT 5;
```
