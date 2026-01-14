"""MealPlan model."""

import uuid
from datetime import date, datetime
from typing import Any

from sqlalchemy import Column, DateTime, Index, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class MealPlan(SQLModel, table=True):
    """Meal plan model with embedded day/meal structure."""

    __tablename__ = "meal_plans"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
    )
    user_id: uuid.UUID = Field(index=True)
    baby_profile_id: uuid.UUID = Field(index=True)
    start_date: date
    num_days: int = Field(ge=3, le=7)  # 3 or 7
    plan_style: str = Field(max_length=20)  # variety, simple_repeats
    introduce_new_foods: bool = Field(default=False)
    days: list[dict[str, Any]] = Field(
        sa_column=Column(JSONB),
    )  # See Days Schema in data-model.md
    shopping_list: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB),
    )
    prep_suggestions: list[dict[str, Any]] = Field(
        default_factory=list,
        sa_column=Column(JSONB),
    )
    schema_version: int = Field(default=1)
    generation_metadata: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB),
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )

    class Config:
        """Pydantic config."""

        arbitrary_types_allowed = True

    # Indexes
    __table_args__ = (
        Index("ix_meal_plans_user_start_date", "user_id", "start_date"),
        Index("ix_meal_plans_baby_profile", "baby_profile_id"),
    )


