# Scalability — Handling Millions of Posts and Reads

Every design decision in Threadline's data layer was made with high-volume read workloads in mind. This document explains each decision and why naïve alternatives would fail at scale.

---

## Problem Space

A social feed at scale faces three hard problems:

| Problem | Naïve approach | Why it fails |
|---|---|---|
| Reading newest posts first | `SELECT * FROM posts ORDER BY created_at DESC OFFSET 100` | OFFSET forces Postgres to scan and discard N rows. At offset 10,000 that's 10,000 wasted row reads on every page load |
| Counting likes/comments | `SELECT COUNT(*) FROM post_likes WHERE post_id = $1` | COUNT(*) acquires a table lock and scans the index on every feed render. With 1M likes per post, this is unbearable |
| Checking if current user liked a post | `SELECT EXISTS (...)` for every post in the feed | N+1 query problem — 10 posts = 10 separate DB round-trips |

---

## Solution 1: Cursor-Based Pagination

### What we use

```python
# routers/posts.py — feed endpoint
stmt = (
    select(Post, User)
    .join(User, Post.user_id == User.id)
    .where(
        (Post.visibility == "public") | (Post.user_id == current_user.id)
    )
)
if cursor:
    cursor_dt = datetime.fromisoformat(cursor)
    stmt = stmt.where(Post.created_at < cursor_dt)  # ← cursor condition

stmt = stmt.order_by(Post.created_at.desc()).limit(limit)
```

The frontend passes the `created_at` of the last post it received as the next cursor:

```typescript
// hooks/usePosts.ts
getNextPageParam: (lastPage) => {
  if (!lastPage || lastPage.length < 10) return undefined;
  return lastPage[lastPage.length - 1].created_at;  // ← ISO timestamp as cursor
}
```

### Why this works at scale

```
OFFSET approach:         Cursor approach:
──────────────────────   ──────────────────────────────
Page 1:  scan rows 1-10  Page 1:  WHERE created_at < now()  LIMIT 10
Page 2:  scan rows 1-20  Page 2:  WHERE created_at < '2024-01-10T15:30:00'  LIMIT 10
Page N:  scan rows 1-N·10  Page N:  always scans exactly 10 rows
```

The `ix_posts_created_at` B-tree index on `created_at DESC` means the cursor condition `WHERE created_at < :cursor` is resolved by a single B-tree seek — Postgres jumps directly to the right position in the index without reading any other rows.

### The partial index for the public feed

```sql
-- 001_initial_schema.py
CREATE INDEX ix_posts_public_created
  ON posts (created_at DESC)
  WHERE visibility = 'public';
```

Public posts make up the vast majority of the feed. A partial index that only includes `visibility = 'public'` rows is dramatically smaller than a full index, so it fits better in the PostgreSQL shared buffer cache (RAM). Fewer cache misses = faster reads.

---

## Solution 2: Denormalized Counters

### What we use

`posts.like_count`, `posts.comment_count`, `comments.like_count`, `comments.reply_count`, `replies.like_count` are stored directly on the parent row and updated atomically when a like/comment is added or removed.

```python
# routers/likes.py — like a post
session.add(PostLike(post_id=post_id, user_id=current_user.id))
post.like_count = post.like_count + 1   # ← atomic increment
session.add(post)
await session.commit()
```

```python
# routers/comments.py — create a comment
comment = Comment(post_id=post_id, user_id=current_user.id, content=body.content)
session.add(comment)
post.comment_count = post.comment_count + 1  # ← atomic increment in same transaction
session.add(post)
await session.commit()
```

### Why this works at scale

Reading the feed requires `like_count` and `comment_count` for every post. With denormalized counters:

```
Feed query (10 posts):
  SELECT posts.*, users.* FROM posts JOIN users ...
  → 1 query, like_count and comment_count already in the row

Without denormalization (per-post aggregation):
  SELECT COUNT(*) FROM post_likes WHERE post_id = $1
  SELECT COUNT(*) FROM comments WHERE post_id = $1
  → 2 extra queries per post = 20 extra queries for a 10-post page
```

The write cost (one extra column update per like) is trivially small. The read savings are massive because reads vastly outnumber writes on any social platform.

### Consistency guarantee

Both the like insert and the counter update happen in the same SQLAlchemy `session.commit()` transaction. If the commit fails, neither the like row nor the counter change is written. The counter can never drift from the true count due to a partial write.

---

## Solution 3: Strategic Indexes

All indexes are defined in `backend/alembic/versions/001_initial_schema.py`.

| Index | Columns | Type | Query it serves |
|---|---|---|---|
| `ix_users_email` | `email` | B-tree UNIQUE | Login lookup by email |
| `ix_posts_created_at` | `created_at DESC` | B-tree | All feed queries (cursor seek) |
| `ix_posts_user_created` | `(user_id, created_at DESC)` | Composite B-tree | "My posts" queries |
| `ix_posts_public_created` | `created_at DESC WHERE visibility='public'` | Partial B-tree | Public feed — smaller index, better cache hit rate |
| `ix_comments_post_created` | `(post_id, created_at ASC)` | Composite B-tree | Load comments for a post in order |
| `ix_replies_comment_created` | `(comment_id, created_at ASC)` | Composite B-tree | Load replies for a comment in order |
| `uq_post_likes_post_user` | `(post_id, user_id)` | UNIQUE constraint | Prevents double-like, O(1) "did I like this?" |
| `uq_comment_likes_comment_user` | `(comment_id, user_id)` | UNIQUE constraint | Same for comment likes |
| `uq_reply_likes_reply_user` | `(reply_id, user_id)` | UNIQUE constraint | Same for reply likes |

### Why composite indexes matter

For comments: `SELECT ... WHERE post_id = $1 ORDER BY created_at ASC`

Without `ix_comments_post_created`, Postgres would:
1. Scan all comments with `post_id = $1` using the FK index
2. Sort them by `created_at` in memory

With `ix_comments_post_created (post_id, created_at ASC)`, Postgres:
1. Seeks to `post_id = $1` in the index
2. Reads rows already ordered by `created_at` — no sort step needed

---

## Solution 4: Async I/O Throughout

The entire backend is async. FastAPI uses ASGI, the database driver is `asyncpg` (the fastest PostgreSQL driver for Python), and all file I/O uses `aiofiles`.

```python
# database.py
engine = create_async_engine(DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
```

This means a single Uvicorn worker can handle hundreds of concurrent requests while waiting for database responses, instead of blocking a thread per request.

---

## Solution 5: Unique Constraints as a Write Guard

```sql
UNIQUE (post_id, user_id)  -- on post_likes
```

This constraint serves double duty:
1. **Prevents double-likes** without needing application-level locking — the database enforces it atomically.
2. **Enables the `liked_by_me` check** in the feed: `SELECT 1 FROM post_likes WHERE post_id=$1 AND user_id=$2` uses the unique index and returns in O(log n) time regardless of how many total likes exist.

---

## How Far Does This Scale?

| Tier | Current design handles | What breaks first |
|---|---|---|
| Posts feed | ~100M posts/day | Cursor pagination and partial index hold. Disk I/O becomes the limit around 1B+ rows |
| Like counts | Unlimited writes | Counter updates are single-row updates — very fast. Race conditions handled by DB transaction |
| Comments load | ~10M comments/post | Composite index + pagination holds indefinitely |
| Concurrent reads | ~500 req/s per Uvicorn worker | Add more workers (Gunicorn + multiple Uvicorn workers) or horizontal scale |

### Next steps for production scale

1. **Read replicas** — route all `SELECT` queries to a read replica; writes go to primary
2. **Redis cache** for hot feed results (top 100 posts cached for 30s)
3. **CDN** for uploaded images instead of local filesystem
4. **Connection pooling** via PgBouncer between FastAPI and PostgreSQL
5. **Horizontal FastAPI scaling** behind a load balancer (all state is in the DB, so stateless scale-out works)
