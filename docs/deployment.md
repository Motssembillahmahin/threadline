# Deployment Guide — Vercel + Render + Supabase + Cloudinary

This guide walks through hosting Threadline for free using:

| Service | Purpose | Free tier |
|---|---|---|
| [Supabase](https://supabase.com) | PostgreSQL database | 500 MB, unlimited requests |
| [Cloudinary](https://cloudinary.com) | Image storage & CDN | 10 GB storage, 25 credits/month |
| [Render](https://render.com) | FastAPI backend | 750 hrs/month (spins down after 15 min inactivity) |
| [Vercel](https://vercel.com) | Next.js frontend | Unlimited, auto-deploys from GitHub |

**Total cost: $0**

---

## Before You Start

Make sure the code is pushed to GitHub. All four services deploy directly from your repo.

---

## Step 1 — Supabase (Database)

1. Go to [supabase.com](https://supabase.com) → **Start your project** → sign in with GitHub
2. Click **New project**
   - Name: `threadline`
   - Database password: choose a strong password and **save it**
   - Region: pick the closest to you
3. Wait ~2 minutes for the project to provision
4. Go to **Project Settings → Database → Connection string → URI**
5. Copy the URI — it looks like:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxxxxxxxxx.supabase.co:5432/postgres
   ```
6. **Replace `postgresql://` with `postgresql+asyncpg://`** — this is required for the async Python driver:
   ```
   postgresql+asyncpg://postgres:[YOUR-PASSWORD]@db.xxxxxxxxxxxx.supabase.co:5432/postgres
   ```
7. Save this — it's your `DATABASE_URL` for Render.

> Alembic migrations run automatically when the backend starts on Render. You don't need to run them manually.

---

## Step 2 — Cloudinary (Image Storage)

1. Go to [cloudinary.com](https://cloudinary.com) → **Sign up for free**
2. After signing in, go to **Dashboard**
3. Under **Product Environment Credentials**, find **API Environment variable** — it looks like:
   ```
   CLOUDINARY_URL=cloudinary://123456789012345:abcdefghijklmnopqrstuvwxyz@your-cloud-name
   ```
4. Copy the entire value including `cloudinary://` — this is your `CLOUDINARY_URL` for Render.

---

## Step 3 — Render (Backend)

1. Go to [render.com](https://render.com) → **Get Started** → sign in with GitHub
2. Click **New → Web Service**
3. Connect your GitHub repo (`threadline`)
4. Configure:

   | Setting | Value |
   |---|---|
   | **Name** | `threadline-backend` |
   | **Root Directory** | `backend` |
   | **Runtime** | `Python 3` |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
   | **Instance Type** | Free |

5. Click **Advanced → Add Environment Variable** and add all of these:

   | Key | Value |
   |---|---|
   | `DATABASE_URL` | Your Supabase URL from Step 1 |
   | `ACCESS_SECRET` | Any random 32+ character string |
   | `REFRESH_SECRET` | Any different random 32+ character string |
   | `CLOUDINARY_URL` | Your Cloudinary URL from Step 2 |
   | `ENVIRONMENT` | `production` |
   | `CORS_ORIGINS` | `https://your-app.vercel.app` ← fill in after Step 4 |
   | `UPLOAD_DIR` | `/tmp/uploads` |

   > You won't know the Vercel URL yet — use a placeholder for now and update it after Step 4.

   **Generating secrets:** Run this in your terminal to generate secure random strings:
   ```bash
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```
   Run it twice — once for `ACCESS_SECRET`, once for `REFRESH_SECRET`.

6. Click **Create Web Service**
7. Wait for the first deploy to finish (~3–5 minutes)
8. Copy your backend URL — it looks like `https://threadline-backend.onrender.com`

> **Note:** The free Render instance spins down after 15 minutes of inactivity. The first request after a sleep takes ~30 seconds. This is normal for free tier.

---

## Step 4 — Vercel (Frontend)

1. Go to [vercel.com](https://vercel.com) → **Sign up** → sign in with GitHub
2. Click **Add New → Project**
3. Import your `threadline` repository
4. Configure:

   | Setting | Value |
   |---|---|
   | **Root Directory** | `frontend` |
   | **Framework Preset** | Next.js (auto-detected) |

5. Click **Environment Variables** and add:

   | Key | Value |
   |---|---|
   | `NEXT_PUBLIC_API_URL` | `https://threadline-backend.onrender.com` (from Step 3) |
   | `NEXT_PUBLIC_MEDIA_URL` | `https://threadline-backend.onrender.com/static/uploads` |

6. Click **Deploy**
7. Wait ~2 minutes for the build to finish
8. Copy your Vercel URL — it looks like `https://threadline.vercel.app`

---

## Step 5 — Wire CORS (Connect Frontend → Backend)

Now that you have both URLs:

1. Go back to **Render → threadline-backend → Environment**
2. Update `CORS_ORIGINS` to your actual Vercel URL:
   ```
   https://threadline.vercel.app
   ```
3. Click **Save Changes** — Render will redeploy automatically (~2 minutes)

---

## Step 6 — Verify Everything Works

Open your Vercel URL (`https://threadline.vercel.app`) and run through this checklist:

- [ ] `/feed` redirects to `/login` (route protection works)
- [ ] Register with a new account → redirects to `/feed`
- [ ] Create a text post → appears at top of feed
- [ ] Create a post with an image → image loads from Cloudinary URL
- [ ] Like the post → count increments
- [ ] Click the like count → WhoLikedModal shows your name
- [ ] Add a comment → appears below post
- [ ] Add a reply → nested below comment
- [ ] Dark mode toggle → layout switches
- [ ] Logout → redirected to `/login`
- [ ] Visit `/feed` directly while logged out → redirected to `/login`

---

## Environment Variables Reference

### Render (Backend)

| Variable | Description | Example |
|---|---|---|
| `DATABASE_URL` | Supabase connection string (asyncpg) | `postgresql+asyncpg://postgres:pass@...` |
| `ACCESS_SECRET` | JWT signing secret (32+ chars) | `a3f8e1...` |
| `REFRESH_SECRET` | JWT refresh signing secret (32+ chars) | `b9c2d4...` |
| `CLOUDINARY_URL` | Full Cloudinary env URL | `cloudinary://key:secret@cloudname` |
| `ENVIRONMENT` | Must be `production` | `production` |
| `CORS_ORIGINS` | Your Vercel URL | `https://threadline.vercel.app` |
| `UPLOAD_DIR` | Temp dir (ephemeral, Cloudinary is used instead) | `/tmp/uploads` |

### Vercel (Frontend)

| Variable | Description | Example |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | Render backend URL | `https://threadline-backend.onrender.com` |
| `NEXT_PUBLIC_MEDIA_URL` | Backend static uploads path | `https://threadline-backend.onrender.com/static/uploads` |

---

## Troubleshooting

**Login fails with a CORS error**
- Check that `CORS_ORIGINS` on Render exactly matches your Vercel URL (no trailing slash)
- Redeploy the backend after updating

**Images don't appear after uploading**
- Check that `CLOUDINARY_URL` is set correctly on Render
- The value must start with `cloudinary://` (not `CLOUDINARY_URL=`)

**"token_expired" loop / can't stay logged in**
- Cookies require `ENVIRONMENT=production` to be set on Render
- Both Vercel and Render serve over HTTPS by default — this is required for `secure=True` cookies

**Render is slow on first load**
- This is expected on the free tier — it spins down after 15 min inactivity
- First request after sleep takes ~30 seconds while it wakes up
- Subsequent requests are fast

**Supabase connection refused**
- Make sure the URL uses `postgresql+asyncpg://` (not `postgresql://`)
- Check that the password in the URL doesn't contain special characters that need URL-encoding (`@`, `#`, `%` etc.) — URL-encode them if so
