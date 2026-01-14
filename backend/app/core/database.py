"""Database session management."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from app.core.config import settings

# Import models to ensure they're registered
from app.models.baby_profile import BabyProfile  # noqa: F401
from app.models.food_item import FoodItem  # noqa: F401
from app.models.meal_plan import MealPlan  # noqa: F401
from app.models.recipe import Recipe  # noqa: F401
from app.models.user import Base, User  # noqa: F401

# Create async engine
engine = create_async_engine(
    settings.database_url_async,
    echo=settings.debug,
    future=True,
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncSession:
    """Dependency to get database session."""
    async with async_session_maker() as session:
        yield session


async def init_db() -> None:
    """Initialize database tables."""
    async with engine.begin() as conn:
        # Create SQLModel tables
        await conn.run_sync(SQLModel.metadata.create_all)
        # Create SQLAlchemy Base tables (for fastapi-users)
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()

