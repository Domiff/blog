# Blog API

FastAPI project: a blog with JWT authentication, a GraphQL API for posts, comments, profiles and bookmarks, and a SQLAdmin panel.

## Stack

- FastAPI (`backend/main.py` → `create_app()` from `backend/core/setup.py`)
- PostgreSQL 16 and Redis 8 (Docker Compose)
- SQLAlchemy 2 async (asyncpg) + Alembic (`backend/core/database.py`, `migrations/`)
- AuthX, JWT RS256, access 15 min / refresh 30 days (`backend/auth/security.py`)
- Redis — revoked-token blocklist (`revoked:{token}`)
- Strawberry GraphQL — one schema at `/graphql` (`backend/core/schemas/graphql.py`)
- SQLAdmin (`/admin`: Users, Profiles, Posts, Comments, Post bookmarks)

## Layout

```
backend/
  main.py            # app = create_app(), entrypoint for fastapi/uvicorn
  core/
    setup.py         # app factory: routers, GraphQL router, admin
    context.py       # GraphQL context (session, current profile, DataLoaders), rollback-on-error extension
                     # (MaskErrors is attached in schemas/graphql.py)
    permissions.py   # GraphQL permissions (IsAuthenticated)
    schemas/         # rest.py — base Pydantic schemas, graphql.py — merged Strawberry schema
    exceptions/      # rest.py — HTTP exceptions, graphql.py — GraphQL errors with extensions.code
    ...              # settings, database, depends, redis, logging, health
  auth/              # User model, /auth router, service, repository, sqladmin UserAdmin
  profile/           # Profile model, repository, GraphQL types/queries/mutations, DataLoaders,
                     # sqladmin ProfileAdmin
  blog/              # Post and Comment models, status enum, repositories, GraphQL types/queries/mutations,
                     # DataLoaders, require_owner (permissions.py), sqladmin PostAdmin and CommentAdmin
  bookmark/          # PostBookmark model, repository, GraphQL types/queries/mutations, DataLoaders,
                     # require_owner (permissions.py), sqladmin BookmarkAdmin
  admin/             # setup_admin, AdminAuth (email login)
migrations/          # Alembic
keys/                # jwt-private.pem / jwt-public.pem (not committed to git)
docker-compose.yaml  # PostgreSQL, Redis
```

## Data model

- `users` — auth data: email, password hash, `is_active`, `is_superuser`
- `profiles` — one per user (`user_id` unique): `username`, `bio`
- `posts` — `title`, `body`, `status` (`draft` / `published`), `published_at`, `author_id` → `profiles`
- `comments` — `body`, `post_id` → `posts`, `author_id` → `profiles`
- `post_bookmarks` — `owner_id` → `profiles`, `post_id` → `posts`; a profile can bookmark a post once
  (unique `(owner_id, post_id)`)

A profile is created on registration with the username `user_<id>`.
Deleting a user deletes their profile; deleting a profile deletes its posts, comments and bookmarks;
deleting a post deletes its comments and bookmarks (`ON DELETE CASCADE`).
All timestamps are stored as `timestamptz`.

## Endpoints

| Path | What |
|---|---|
| `POST /auth/register` | register `{email, password}` → 201, creates the user's profile |
| `POST /auth/login` | login → access + refresh |
| `POST /auth/logout` | revoke tokens (writes to the Redis blocklist) |
| `POST /auth/refresh` | rotate the pair using the refresh token |
| `/graphql` | GraphQL API (see below), GraphiQL in the browser |
| `/admin` | SQLAdmin, email login (see `backend/admin/auth.py`) |
| `GET /health` | `{"status", "database"}` |
| `/openapi.json` | only when `IS_DEBUG=true` |

## GraphQL

Queries (public):

| Field | Returns |
|---|---|
| `posts` | published posts |
| `postById(postId)` | a post or `null`; drafts are returned only to their author |
| `profiles` | all profiles |
| `profileById(profileId)` / `profileByUsername(username)` | a profile or `null` |
| `commentById(commentId)` | a comment or `null` |
| `bookmarks(ownerId)` | a profile's bookmarks, newest first (bookmarks are public, like on Habr) |

Queries that require a token:

| Field | Returns |
|---|---|
| `myPosts(status)` | the current profile's posts in any status, optionally filtered (`DRAFT` / `PUBLISHED`) |

Related fields are resolved on demand: `Post.author` → `Profile`, `Post.comments` → `[Comment]`,
`Post.commentsCount`, `Comment.author` → `Profile`, `Profile.posts` → `[Post]`, `Profile.postsCount`,
`Profile.bookmarks` → `[PostBookmark]`, `Profile.bookmarksCount`, `PostBookmark.post` → `Post`.

Drafts are visible only to their author: public lists (`posts`, `Profile.posts`, `Profile.postsCount`,
bookmarks) contain only published posts. A bookmark on a post that went back to draft is hidden
until the post is published again.

Mutations (require `Authorization: Bearer <access token>`):

| Field | What |
|---|---|
| `createPost(input)` | create a draft; the author is the current profile |
| `updatePost(postId, input)` | update own post |
| `deletePost(postId)` | delete own post |
| `publishPost(postId)` | publish own draft |
| `createComment(input)` | comment on a published post (`postId`, `body`) |
| `updateComment(commentId, input)` | update own comment |
| `deleteComment(commentId)` | delete own comment |
| `updateProfile(input)` | update the current profile (`username`, `bio`) |
| `createBookmark(input)` | bookmark a post (`postId`); returns the existing bookmark if it is already there |
| `deleteBookmark(postId)` | delete own bookmark |

Example:

```graphql
mutation {
  createPost(input: {title: "Hello", body: "First post"}) {
    id
    status
    author { username }
  }
}
```

```graphql
{
  postById(postId: 1) {
    title
    comments {
      body
      author { username }
    }
  }
}
```

In GraphiQL, put the token on the **Headers** tab:

```json
{"Authorization": "Bearer eyJ..."}
```

Errors come in `errors[]`; application errors carry a code in `extensions.code`
(`FORBIDDEN`, `NOT_FOUND`). Without a token, mutations and `myPosts` return `Authentication required`.
If a request has errors, its transaction is rolled back.

Unexpected server errors (e.g. database errors) are masked as `Unexpected error.` by the
`MaskErrors` extension; details are only in the server logs. Application errors
(`GraphQLError` subclasses from `backend/core/exceptions/graphql.py`) and query validation
errors are returned as is.

### DataLoaders (N+1)

Related fields are loaded through [DataLoaders](https://strawberry.rocks/docs/guides/dataloaders):
resolvers call `loader.load(key)`, and all keys requested on one level of the query are loaded
with a single SQL query (`WHERE ... IN (...)` or `GROUP BY`). The number of SQL queries does not
depend on the number of returned objects.

| Loader | Key → value | Used by | File |
|---|---|---|---|
| `profile_loaders.profile_by_id` | profile id → `Profile` | `Post.author`, `Comment.author` | `profile/loaders.py` |
| `blog_loaders.posts_by_author` | profile id → `[Post]` | `Profile.posts` | `blog/loaders.py` |
| `blog_loaders.posts_count_by_author` | profile id → `int` | `Profile.postsCount` | `blog/loaders.py` |
| `blog_loaders.post_by_id` | post id → `Post` | `PostBookmark.post` | `blog/loaders.py` |
| `blog_loaders.comments_by_post` | post id → `[Comment]` | `Post.comments` | `blog/loaders.py` |
| `blog_loaders.comments_count_by_post` | post id → `int` | `Post.commentsCount` | `blog/loaders.py` |
| `bookmark_loaders.bookmarks_by_owner` | profile id → `[PostBookmark]` | `Profile.bookmarks` | `bookmark/loaders.py` |
| `bookmark_loaders.bookmarks_count_by_owner` | profile id → `int` | `Profile.bookmarksCount` | `bookmark/loaders.py` |

Loaders are created per request in `get_context` (`backend/core/context.py`), so their cache never
leaks between requests. A batch function must return values in the same order and length as the keys.

For example, this query runs 4–5 SQL queries regardless of the number of posts
(without loaders: 1 + 3 per post + 1 per comment). Set `DB_ECHO=true` to see them:

```graphql
{
  posts {
    title
    author { username }
    commentsCount
    comments { body author { username } }
  }
}
```

## Requirements

- Python >= 3.14, `uv`
- Docker (PostgreSQL, Redis)
- Redis is always required: every request with a token checks the blocklist

## Quickstart

```bash
uv sync

# 1. JWT keys (RS256)
mkdir -p keys
openssl genrsa -out keys/jwt-private.pem 2048
openssl rsa -in keys/jwt-private.pem -pubout -out keys/jwt-public.pem

# 2. .env (then edit the values)
cp .env.example .env

# 3. PostgreSQL and Redis (reads POSTGRES_* from .env)
docker compose up -d

# 4. Migrations
uv run alembic upgrade head

# 5. Run
uv run fastapi run backend/main.py
# or: uv run uvicorn backend.main:app --reload
```

Open: API `http://127.0.0.1:8000`, GraphQL `.../graphql`, admin `.../admin`.

## Environment variables

See `.env.example`. Defaults are in `backend/core/settings.py`:

| Variable | Default | Purpose |
|---|---|---|
| `ADMIN_SECRET_KEY` | — (required) | admin session secret |
| `IS_DEBUG` | `true` | enables `/openapi.json` |
| `GRAPHQL_PATH` | `/graphql` | GraphQL endpoint path |
| `POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_PASSWORD` | placeholders | database credentials, also used by Docker Compose |
| `POSTGRES_HOST` / `POSTGRES_PORT` | `localhost` / `5432` | database address (URL assembled in `get_url()`) |
| `DB_ECHO` | `false` | log all SQL queries (for debugging) |
| `REDIS_HOST` / `REDIS_PORT` / `REDIS_DB` | `localhost` / `6379` / `0` | assembled into `REDIS_URL` |
| `ADMIN_BASE_URL` | `/admin` | admin path |
| `LOG_LEVEL` | `INFO` | log level for `backend.*` |

## Migrations

```bash
uv run alembic upgrade head                      # apply
uv run alembic revision --autogenerate -m "msg"  # new
```

Always review autogenerated migrations. Alembic does not detect everything (e.g. some type parameter changes),
and PostgreSQL enum types must be dropped manually in `downgrade()`:

```python
sa.Enum(name="post_status").drop(op.get_bind(), checkfirst=True)
```

## Admin

Login: the user must be active and a superuser (`is_active`, `is_superuser`);
credentials are the email + password from `/auth/register`.

| Section | Notes |
|---|---|
| Users | create (password is hashed), edit, change status |
| Profiles | edit `username` / `bio`; no create or delete — created on registration, deleted with the user |
| Posts | create (author, title, body; created as a draft), edit `title` / `body`, delete |
| Comments | create (post, author, body), edit `body`, delete (moderation) |
| Post bookmarks | create (owner, post), delete; no edit |
