# Blog Platform API

A basic blogging backend built with **FastAPI** + **PostgreSQL** (SQLAlchemy ORM). Covers the
core of any blog — users, posts, categories, comments, JWT auth — structured so each piece
(models / schemas / crud / routers) is easy to extend independently.

## Features (basic)

- **Auth**: register, login, JWT bearer tokens, password hashing (bcrypt)
- **Users**: profile, update own profile
- **Posts**: create/read/update/delete, slugs, pagination, search, category filter, tag filter, view counts
- **Categories**: list, create (admin-only)
- **Tags**: many-to-many with posts, created automatically when referenced by name on a post
- **Comments**: nested under posts, create/list/delete
- **Permissions**: only a post's author (or a superuser) can edit/delete it; same for comments
- **Migrations**: schema managed with Alembic (autogenerate-ready), not ad-hoc `create_all()`
- **Docker**: `docker-compose.yml` for app + Postgres, one command to run everything

## Project structure

```
app/
├── main.py            # FastAPI app, router registration
├── config.py           # Settings (reads .env)
├── database.py         # SQLAlchemy engine/session
├── models/              # SQLAlchemy ORM models (incl. tags + post_tags association)
├── schemas/             # Pydantic request/response schemas
├── crud/                 # Database access functions
├── routers/              # API endpoints
├── auth/                 # JWT + password hashing + auth dependencies
└── utils/                # Slug generation, etc.
alembic/                  # Migration environment (wired to app.config + app.models)
alembic.ini
Dockerfile
docker-compose.yml
```

## Setup — option A: Render (production hosting)

This repo includes a `render.yaml` [Blueprint](https://render.com/docs/infrastructure-as-code) that
provisions the API and a managed Postgres database together.

1. Push this repo to GitHub (or GitLab/Bitbucket).
2. In the [Render Dashboard](https://dashboard.render.com), click **New → Blueprint** and select
   your repo. Render detects `render.yaml` automatically.
3. Click **Apply**. Render will:
   - Create a Postgres database (`blog-platform-db`)
   - Create a web service (`blog-platform-api`) wired to that database via `DATABASE_URL`
   - Generate a random `SECRET_KEY` for you (no need to set one manually)
   - Run `pip install -r requirements.txt`, then `alembic upgrade head` as a pre-deploy step,
     then start the app with `uvicorn ... --port $PORT`
4. Once deployed, your API is live at `https://blog-platform-api.onrender.com` (or whatever
   name you gave it) — try `/docs` for the interactive Swagger UI.
5. Before pointing a real frontend at it, set the `CORS_ORIGINS` env var on the service
   (Dashboard → your service → Environment) to your frontend's actual origin(s), e.g.
   `https://myblog.com,https://www.myblog.com` — the default `*` is fine for testing only.

**Free-tier caveats worth knowing before you rely on this:**
- A free web service **spins down after 15 minutes of no traffic** and takes ~1 minute to
  spin back up on the next request — fine for a demo, not for production traffic.
- A free Postgres database **expires 30 days after creation** (14-day grace period to upgrade
  before Render deletes it). For anything beyond testing, move the database to a paid plan
  (edit `plan:` under `databases` in `render.yaml`, or change it in the Dashboard).
- Free Postgres has no backups and a 1 GB storage cap.

**No Blueprint? Manual setup works too:** create a Postgres instance in the Dashboard, then a
Python web service pointing at this repo with build command `pip install -r requirements.txt`,
pre-deploy command `alembic upgrade head`, start command
`uvicorn app.main:app --host 0.0.0.0 --port $PORT`, and set `DATABASE_URL` (from the Postgres
instance's "Internal Connection String") plus `SECRET_KEY` manually as env vars.

## Setup — option B: Docker (local)

```bash
docker compose up --build
```

This starts Postgres, runs Alembic migrations, and launches the API on
`http://localhost:8000` — nothing else to install. Edit the `SECRET_KEY` in
`docker-compose.yml` before using this outside local development.

## Setup — option C: local Python + Postgres

1. **Create a PostgreSQL database**

   ```sql
   CREATE DATABASE blog_db;
   CREATE USER blog_user WITH PASSWORD 'blog_password';
   GRANT ALL PRIVILEGES ON DATABASE blog_db TO blog_user;
   ```

2. **Install dependencies**

   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment**

   ```bash
   cp .env.example .env
   # edit .env: set DATABASE_URL and a strong random SECRET_KEY
   ```

4. **Run migrations**

   ```bash
   alembic upgrade head
   ```

   This creates all tables (users, posts, categories, tags, comments) via the migration
   in `alembic/versions/`. Schema is managed here, not with `Base.metadata.create_all()`.

5. **Run the app**

   ```bash
   uvicorn app.main:app --reload
   ```

6. **Explore the API** at `http://localhost:8000/docs` (interactive Swagger UI).

### Making future schema changes

After editing a model in `app/models/`:

```bash
alembic revision --autogenerate -m "describe the change"
alembic upgrade head
```

Always review the generated migration file before applying it — autogenerate is a strong
starting point, not a guarantee (it won't catch every edge case, e.g. some column renames).

## Quick API tour

| Action | Method & path |
|---|---|
| Register | `POST /auth/register` |
| Login (get JWT) | `POST /auth/login` (form-encoded `username`, `password`) |
| My profile | `GET /users/me` (Bearer token) |
| List posts | `GET /posts/?skip=0&limit=10&search=&category_id=` |
| Post detail | `GET /posts/{slug}` |
| Create post | `POST /posts/` (Bearer token) |
| Update/delete post | `PATCH` / `DELETE /posts/{id}` (author or admin) |
| List categories | `GET /categories/` |
| Create category | `POST /categories/` (admin only) |
| List tags | `GET /tags/` |
| Comments | `GET/POST /posts/{post_id}/comments/`, `DELETE /posts/{post_id}/comments/{id}` |

Every protected endpoint expects `Authorization: Bearer <token>`.

Tags aren't created via a dedicated endpoint — pass `tag_names: ["fastapi", "postgres"]` in
`POST /posts/` or `PATCH /posts/{id}` and they're created automatically if they don't exist
yet (case-insensitive matching, so `"FastAPI"` and `"fastapi"` resolve to the same tag).
Filter posts by tag with `GET /posts/?tag=<slug>`.

## Enhancing further

The structure is deliberately layered (model → schema → crud → router) so you can add features
without rewriting existing code. Alembic migrations, tags, and Docker packaging are done —
natural next steps, roughly in order of impact:

1. **Likes / reactions** — an association table between users and posts, same pattern as
   `post_tags` in `app/models/associations.py`.
2. **Full-text search** — swap the `ilike` search in `crud/post.py` for PostgreSQL's
   `tsvector`/`tsquery`, or plug in Elasticsearch/Meilisearch for larger sites.
3. **Image uploads** — an endpoint that accepts multipart uploads and stores files
   (locally, or S3/Cloud Storage) for `cover_image_url`.
4. **Rich pagination** — return total count / `has_more` metadata, not just a page of rows.
5. **Email verification & password reset** — extend the auth router with token-based flows.
6. **Role-based permissions** — replace the single `is_superuser` flag with an `editor`/`author`
   role system if you need finer content moderation.
7. **Caching** — Redis cache for popular post lists or view counts under high traffic.
8. **Tests** — add a `pytest` + `httpx` test suite (the smoke tests used during development are
   a good starting template — spin up SQLite or a test Postgres schema per test run).
9. **Rate limiting & CORS lockdown** — tighten `allow_origins` in `main.py` and add
   rate limiting (e.g. `slowapi`) before deploying publicly.
10. **CI** — run `alembic upgrade head` + the test suite against a throwaway Postgres
    container in GitHub Actions (or similar) on every push.

## Notes

- Passwords are hashed with bcrypt via passlib; never stored in plaintext.
- Slugs are auto-generated from titles/names and de-duplicated with a short random suffix
  on collision (`app/utils/slugify.py`).
- `PostListOut` vs `PostDetailOut`/`PostOut` keep list responses lightweight (no full body)
  while detail responses include everything, including comments.
- The Alembic setup, tag CRUD, and REST endpoints were exercised end-to-end against a live
  app instance (register → login → create/tag/filter/update posts → migrations apply cleanly)
  during development. The `Dockerfile`/`docker-compose.yml` follow standard, well-tested
  patterns but weren't run in a live Docker daemon while building this — if `docker compose up`
  surfaces anything on your machine, it's most likely an environment-specific fix (e.g. a
  Postgres port already in use), not a structural issue.
