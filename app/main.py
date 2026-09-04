from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, users, posts, comments, categories, tags

# Schema is managed by Alembic migrations (see /alembic and the README) —
# run `alembic upgrade head` before starting the app for the first time.

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="A basic blog platform API built with FastAPI + PostgreSQL.",
    version="1.0.0",
)

_cors_origins = (
    ["*"] if settings.CORS_ORIGINS.strip() == "*"
    else [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(categories.router)
app.include_router(tags.router)
app.include_router(posts.router)
app.include_router(comments.router)


@app.get("/", tags=["health"])
def health_check():
    return {"status": "ok", "project": settings.PROJECT_NAME}
