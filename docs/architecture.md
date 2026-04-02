# System Architecture

## Overview

Threadline is a three-tier web application. Each tier runs in its own Docker container and communicates over a private Docker network.

```
Browser
  │
  ├── GET  http://localhost:3000  →  Next.js (frontend)
  │         │
  │         └── /api/* rewrites  →  FastAPI (backend)  →  PostgreSQL (db)
  │                                       │
  │                                  /static/uploads
  │                                  (served directly)
  └── static assets (CSS/JS/images) served from Next.js public/
```

---

## Tech Stack

| Layer | Technology | Version | Why |
|---|---|---|---|
| Frontend | Next.js (App Router) | 14 | Server Components, edge middleware, standalone build |
| Language | TypeScript | 5 | Type safety across all frontend code |
| Backend | FastAPI | 0.115 | Async-first Python, automatic OpenAPI docs |
| Runtime | Uvicorn | 0.32 | ASGI server with async worker support |
| ORM | SQLModel + SQLAlchemy async | 0.0.22 / 2.0 | Pydantic models that are also DB tables |
| Migrations | Alembic | 1.14 | Schema versioning, rollback support |
| Database | PostgreSQL | 16 | ACID, partial indexes, UUID gen |
| Auth | JWT (python-jose) | HS256 | Stateless tokens, httpOnly cookies |
| Password | passlib[bcrypt] | 1.7 | Adaptive cost factor, salted hashes |
| Data fetching | TanStack React Query | 5 | Cache, deduplication, optimistic updates |
| HTTP client | Axios | 1.x | Interceptors for silent token refresh |
| Container | Docker + Compose | v2 | Reproducible environments, healthchecks |

---

## Directory Structure

```
threadline/
├── Makefile                      # Developer commands
├── docker-compose.yml            # Service orchestration
├── .env.example                  # Environment variable template
├── docs/                         # Project documentation
│   ├── architecture.md           # ← this file
│   ├── scalability.md            # Millions of posts strategy
│   ├── frontend-workflow.md      # Next.js data flow and auth
│   └── html-to-nextjs.md        # Design preservation guide
│
├── backend/
│   ├── Dockerfile                # python:3.12-slim multi-stage
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── alembic/
│   │   └── versions/
│   │       └── 001_initial_schema.py
│   └── app/
│       ├── main.py               # FastAPI app: CORS, StaticFiles, routers
│       ├── config.py             # Settings from env vars (pydantic-settings)
│       ├── database.py           # Async engine + get_session dependency
│       ├── models/               # SQLModel table classes
│       │   ├── user.py
│       │   ├── post.py
│       │   ├── comment.py
│       │   ├── reply.py
│       │   └── like.py           # PostLike, CommentLike, ReplyLike
│       ├── schemas/              # Pydantic request/response shapes
│       │   ├── auth.py
│       │   ├── post.py
│       │   └── comment.py
│       ├── routers/              # One file per resource
│       │   ├── auth.py           # register, login, logout, refresh, me
│       │   ├── posts.py          # CRUD + cursor-paginated feed
│       │   ├── comments.py
│       │   ├── replies.py
│       │   └── likes.py          # post/comment/reply likes + who-liked
│       ├── services/
│       │   ├── auth_service.py   # bcrypt hash/verify, JWT create/decode
│       │   └── upload_service.py # image validation, UUID filename, save
│       └── middleware/
│           └── auth_middleware.py # get_current_user FastAPI dependency
│
└── frontend/
    ├── Dockerfile                # node:20-alpine multi-stage standalone
    ├── next.config.ts            # rewrites, image domains, standalone output
    ├── src/
    │   ├── middleware.ts         # Edge route guard (access_token cookie)
    │   ├── app/
    │   │   ├── layout.tsx        # Root layout: Poppins font, Providers
    │   │   ├── providers.tsx     # QueryClientProvider + AuthProvider
    │   │   ├── globals.css       # @import original 4 CSS files
    │   │   ├── page.tsx          # Root redirect → /feed
    │   │   ├── (auth)/
    │   │   │   ├── login/page.tsx
    │   │   │   └── register/page.tsx
    │   │   └── feed/
    │   │       └── page.tsx      # Server Component, checks cookie
    │   ├── components/
    │   │   ├── auth/             # LoginForm, RegisterForm
    │   │   ├── layout/           # Navbar, LeftSidebar, RightSidebar
    │   │   ├── feed/             # PostFeed, PostCard, CreatePostBox,
    │   │   │                     # CommentSection, CommentItem, ReplyItem,
    │   │   │                     # WhoLikedModal, StoriesCarousel
    │   │   └── ui/               # DarkModeToggle
    │   ├── context/
    │   │   └── AuthContext.tsx   # Global user state, bootstrap /api/auth/me
    │   ├── hooks/
    │   │   ├── usePosts.ts       # Infinite query + create/delete mutations
    │   │   ├── useComments.ts    # List + create comment
    │   │   └── useReplies.ts     # List + create reply
    │   ├── lib/
    │   │   └── api.ts            # Axios instance + 401 refresh interceptor
    │   └── types/
    │       └── index.ts          # TypeScript interfaces
    └── public/
        └── assets/               # Original CSS/JS/images (copied verbatim)
```

---

## Database Schema

All primary keys are UUID (generated by PostgreSQL `gen_random_uuid()`). Timestamps use `TIMESTAMPTZ`.

### Entity Relationship

```
users (1) ──< posts (N)
posts (1) ──< comments (N)
comments (1) ──< replies (N)

posts (1) ──< post_likes (N) >── (1) users
comments (1) ──< comment_likes (N) >── (1) users
replies (1) ──< reply_likes (N) >── (1) users
```

### Table Details

**users**
```sql
id           UUID PK   DEFAULT gen_random_uuid()
first_name   VARCHAR(100)  NOT NULL
last_name    VARCHAR(100)  NOT NULL
email        VARCHAR(255)  NOT NULL  UNIQUE  -- INDEX ix_users_email
password_hash VARCHAR(255) NOT NULL
avatar_url   VARCHAR(500)  NULLABLE
created_at   TIMESTAMPTZ   DEFAULT now()
```

**posts**
```sql
id           UUID PK
user_id      UUID FK→users   ON DELETE CASCADE
content      TEXT            NULLABLE
image_url    VARCHAR(500)    NULLABLE
visibility   VARCHAR(10)     DEFAULT 'public'  CHECK IN ('public','private')
like_count   INT             DEFAULT 0         -- denormalized
comment_count INT            DEFAULT 0         -- denormalized
created_at   TIMESTAMPTZ     DEFAULT now()

INDEX ix_posts_created_at         ON (created_at DESC)
INDEX ix_posts_user_created       ON (user_id, created_at DESC)
INDEX ix_posts_public_created     ON (created_at DESC) WHERE visibility='public'
```

**comments**
```sql
id           UUID PK
post_id      UUID FK→posts   ON DELETE CASCADE
user_id      UUID FK→users   ON DELETE CASCADE
content      TEXT            NOT NULL
like_count   INT             DEFAULT 0
reply_count  INT             DEFAULT 0   -- denormalized
created_at   TIMESTAMPTZ

INDEX ix_comments_post_created    ON (post_id, created_at ASC)
```

**replies**
```sql
id           UUID PK
comment_id   UUID FK→comments  ON DELETE CASCADE
user_id      UUID FK→users     ON DELETE CASCADE
content      TEXT              NOT NULL
like_count   INT               DEFAULT 0
created_at   TIMESTAMPTZ

INDEX ix_replies_comment_created  ON (comment_id, created_at ASC)
```

**post_likes / comment_likes / reply_likes**
```sql
id           UUID PK
{target}_id  UUID FK→{target}  ON DELETE CASCADE
user_id      UUID FK→users     ON DELETE CASCADE
created_at   TIMESTAMPTZ

UNIQUE (post_id, user_id)        -- prevents double-like, enables O(1) lookup
```

---

## API Endpoints

Base URL: `http://localhost:8000`

All authenticated endpoints require the `access_token` httpOnly cookie.

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/auth/register` | No | Register user, set JWT cookies |
| POST | `/api/auth/login` | No | Login, set JWT cookies |
| POST | `/api/auth/logout` | No | Clear JWT cookies |
| POST | `/api/auth/refresh` | Cookie | Issue new access_token from refresh_token |
| GET | `/api/auth/me` | Yes | Return current user |
| GET | `/api/posts?cursor=&limit=10` | Yes | Cursor-paginated feed |
| POST | `/api/posts` | Yes | Create post (multipart/form-data) |
| GET | `/api/posts/{id}` | Yes | Single post (403 if private + not owner) |
| PATCH | `/api/posts/{id}` | Yes + owner | Edit content/visibility |
| DELETE | `/api/posts/{id}` | Yes + owner | Delete post |
| GET | `/api/comments/post/{id}` | Yes | List comments for post |
| POST | `/api/comments/post/{id}` | Yes | Create comment |
| DELETE | `/api/comments/{id}` | Yes + owner | Delete comment |
| GET | `/api/replies/comment/{id}` | Yes | List replies for comment |
| POST | `/api/replies/comment/{id}` | Yes | Create reply |
| DELETE | `/api/replies/{id}` | Yes + owner | Delete reply |
| POST | `/api/likes/post/{id}` | Yes | Like post |
| DELETE | `/api/likes/post/{id}` | Yes | Unlike post |
| GET | `/api/likes/post/{id}/users` | Yes | Who liked this post |
| POST/DELETE/GET | `/api/likes/comment/{id}[/users]` | Yes | Same for comments |
| POST/DELETE/GET | `/api/likes/reply/{id}[/users]` | Yes | Same for replies |
| GET | `/api/health` | No | Health check |

---

## Authentication Flow

```
┌─────────┐          ┌──────────┐         ┌──────────┐
│ Browser │          │ Next.js  │         │ FastAPI  │
└────┬────┘          └────┬─────┘         └────┬─────┘
     │                    │                     │
     │  POST /login        │                     │
     ├───────────────────►│                     │
     │                    │  POST /api/auth/login│
     │                    ├────────────────────►│
     │                    │  Set-Cookie:         │
     │                    │  access_token (15m)  │
     │                    │  refresh_token (7d)  │
     │                    │◄────────────────────┤
     │  Set-Cookie (httpOnly, samesite=lax)      │
     │◄───────────────────┤                     │
     │                    │                     │
     │  GET /api/posts     │                     │
     │  Cookie: access_token                    │
     ├───────────────────────────────────────►  │
     │                                          │ Decode JWT
     │                                          │ Lookup user
     │◄────────────────────────────────────────┤
     │                    │                     │
     │  GET /api/posts [access expired]         │
     │  ← 401 detail:"token_expired"           │
     │  Axios interceptor fires                 │
     │  POST /api/auth/refresh (refresh cookie) │
     ├───────────────────────────────────────►  │
     │  New access_token cookie                │
     │◄────────────────────────────────────────┤
     │  Retry original request                  │
     ├───────────────────────────────────────►  │
```

**Token details:**
- Access token: HS256, 15-minute expiry, `ACCESS_SECRET`
- Refresh token: HS256, 7-day expiry, `REFRESH_SECRET`, cookie scoped to `path=/api/auth/refresh`
- Both cookies: `httpOnly=true`, `samesite=lax`, `secure=false` (enable in production)

---

## Docker Services

```yaml
db:       postgres:16-alpine  — port 5432, healthcheck pg_isready
backend:  python:3.12-slim    — port 8000, waits for db healthy
frontend: node:20-alpine      — port 3000, standalone build
```

The `backend` service runs `alembic upgrade head` before starting Uvicorn. This means the database is always migrated to the latest schema on container start.

Network: all three services share a default Docker bridge network. The backend connects to `db:5432`. The frontend calls `backend:8000` server-side (via Next.js rewrites) and `localhost:8000` client-side (via browser).
