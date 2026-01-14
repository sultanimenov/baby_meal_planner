"""FastAPI application entry point."""

import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI

# Configure logging for planner state transitions
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stdout,
)
# Ensure planner logs are visible
logging.getLogger("app.planner").setLevel(logging.INFO)
# Reduce noise from other libs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, logs, plans, profiles
from app.core.config import settings
from app.core.database import close_db, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()


app = FastAPI(
    title="Infant Meal Planner API",
    description="API for planning and managing complementary feeding meals for babies",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(profiles.router, prefix="/baby-profile", tags=["profile"])
app.include_router(plans.router, prefix="/plans", tags=["plans"])
app.include_router(logs.router, prefix="/logs", tags=["logs"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/health/db")
async def health_db():
    """Database health check endpoint."""
    from sqlalchemy import text

    from app.core.database import engine

    async with engine.connect() as conn:
        result = await conn.execute(
            text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public'"
            )
        )
        tables = [row[0] for row in result.fetchall()]
    return {"status": "ok", "tables": tables}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Infant Meal Planner API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/recipes")
async def list_recipes():
    """List all recipes (public endpoint for verification)."""
    from sqlalchemy import select

    from app.core.database import engine
    from app.models.recipe import Recipe

    async with engine.connect() as conn:
        from sqlalchemy.ext.asyncio import AsyncSession

        async with AsyncSession(bind=conn) as session:
            result = await session.execute(select(Recipe))
            recipes = result.scalars().all()
            return [
                {
                    "id": str(r.id),
                    "title": r.title,
                    "min_age_months": r.min_age_months,
                    "texture_level": r.texture_level,
                }
                for r in recipes
            ]

