"""Logging models for meal outcomes and reactions."""

import uuid
from datetime import date, datetime

from sqlalchemy import Column, DateTime, Index, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class MealLog(SQLModel, table=True):
    """Log of meal outcomes for each meal slot."""

    __tablename__ = "meal_logs"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
    )
    user_id: uuid.UUID = Field(index=True)
    baby_profile_id: uuid.UUID = Field(index=True)
    meal_plan_id: uuid.UUID | None = Field(default=None, index=True)
    date: date
    meal_slot: str = Field(max_length=20)  # breakfast, lunch, dinner, snack
    recipe_id: uuid.UUID | None = Field(default=None, index=True)
    outcome: str = Field(max_length=20)  # ate, partial, refused
    notes: str | None = Field(default=None)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )

    class Config:
        """Pydantic config."""

        arbitrary_types_allowed = True

    __table_args__ = (
        Index("ix_meal_logs_baby_profile_date", "baby_profile_id", "date"),
        Index("ix_meal_logs_recipe", "recipe_id"),
    )


class ReactionLog(SQLModel, table=True):
    """Log of suspected allergic or adverse reactions."""

    __tablename__ = "reaction_logs"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
    )
    user_id: uuid.UUID = Field(index=True)
    baby_profile_id: uuid.UUID = Field(index=True)
    occurred_at: datetime
    symptoms: str
    severity: str = Field(default="mild", max_length=20)  # mild, moderate, severe
    suspected_food_ids: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSONB),
    )
    suspected_recipe_ids: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSONB),
    )
    notes: str | None = Field(default=None)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )

    class Config:
        """Pydantic config."""

        arbitrary_types_allowed = True

    __table_args__ = (
        Index("ix_reaction_logs_baby_profile_occurred", "baby_profile_id", "occurred_at"),
    )


