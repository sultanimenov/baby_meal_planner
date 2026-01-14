"""User model for authentication."""

from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""

    pass


class User(SQLAlchemyBaseUserTableUUID, Base):
    """User model managed by fastapi-users."""

    __tablename__ = "users"
