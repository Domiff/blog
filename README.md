# Blog API

FastAPI project: a blog with JWT authentication, GraphQL for posts, and a SQLAdmin panel.

## Stack

- FastAPI (`backend/main.py` → `create_app()` from `backend/core/setup.py`)
- SQLAlchemy 2 async + Alembic (`backend/core/database.py`, `migrations/`)
- AuthX, JWT RS256, access 15 min / refresh 30 days (`backend/auth/security.py`)
- Redis — revoked-token blocklist (`revoked:{token}`)
- Strawberry GraphQL (`/graphql`)
- SQLAdmin (`/admin`, Users and Posts sections)

## Layout

```
backend/
  main.py            # app = create_app(), entrypoint for fastapi/uvicorn
  core/              # setup, settings, database, redis, logging, health
  auth/              # models, /auth router, service, repository, sqladmin UserAdmin
  blog/              # models, GraphQL schema/router, repository, sqladmin PostAdmin
  admin/             # setup_admin, AdminAuth (email login)
migrations/          # Alembic
keys/                # jwt-private.pem / jwt-public.pem (not committed to git)
```

## Endpoints

| Path | What |
|---|---|
| `POST /auth/register` | register `{email, password}` → 201 |
| `POST /auth/login` | login → access + refresh |
| `POST /auth/logout` | revoke tokens (writes to the Redis blocklist) |
| `POST /auth/refresh` | rotate the pair using the refresh token |
| `/graphql` | `get_post_list`, `get_post_by_id`, `create_post`, `update_post`, `delete_post` |
| `/admin` | SQLAdmin, email login (see `backend/admin/auth.py`) |
| `GET /health` | `{"status", "database"}` |
| `/openapi.json` | only when `IS_DEBUG=true` |

## Requirements

- Python >= 3.14, `uv`
- Redis on `localhost:6379` (always required — blocklist check in `security.py`)
- SQLite locally (`IS_DEBUG=true`), PostgreSQL in prod (`IS_DEBUG=false`)

## Quickstart

```bash
uv sync

# 1. JWT keys (RS256)
mkdir -p keys
openssl genrsa -out keys/jwt-private.pem 2048
openssl rsa -in keys/jwt-private.pem -pubout -out keys/jwt-public.pem

# 2. Redis
docker run -d -p 6379:6379 redis:7

# 3. .env
cat > .env <<EOF
ADMIN_SECRET_KEY=change-me
EOF

# 4. Migrations
uv run alembic upgrade head

# 5. Run
uv run fastapi run backend/main.py
# or: uv run uvicorn backend.main:app --reload
```

Open: API `http://127.0.0.1:8000`, GraphQL `.../graphql`, admin `.../admin`.

## Environment variables

Only `ADMIN_SECRET_KEY` is required. Everything else has defaults (`backend/core/settings.py`):

| Variable | Default | Purpose |
|---|---|---|
| `ADMIN_SECRET_KEY` | — | admin session secret |
| `IS_DEBUG` | `true` | `true` → SQLite, `false` → PostgreSQL |
| `DB_URL` | empty | override the whole DB URL |
| `SQLITE_URL` | `sqlite+aiosqlite:///db.sqlite3` | local database |
| `POSTGRES_*` | `localhost:5432`, placeholders | prod database (assembled in `get_pg_url()`) |
| `REDIS_HOST/PORT/DB` | `localhost/6379/0` | assembled into `REDIS_URL` |
| `ADMIN_BASE_URL` | `/admin` | admin path |
| `LOG_LEVEL` | `INFO` | log level for `backend.*` |

## Migrations

```bash
uv run alembic upgrade head                    # apply
uv run alembic revision --autogenerate -m "msg"  # new
```

Admin login: the user must exist in the DB and be active (`is_active`); credentials are the email + password from `/auth/register`.
