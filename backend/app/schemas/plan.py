"""Pydantic schemas for meal plans."""

import uuid
from datetime import date, datetime
from typing import Any

from pydantic import Field
from sqlmodel import SQLModel


class MealPlanCreate(SQLModel):
    """Schema for creating a meal plan request."""

    num_days: int = Field(ge=3, le=7, description="3 or 7 days")
    plan_style: str = Field(pattern="^(variety|simple_repeats)$")
    introduce_new_foods: bool = Field(default=False)


class MealPlanRead(SQLModel):
    """Schema for reading a meal plan."""

    id: uuid.UUID
    user_id: uuid.UUID
    baby_profile_id: uuid.UUID
    start_date: date
    num_days: int
    plan_style: str
    introduce_new_foods: bool
    days: list[dict[str, Any]]
    shopping_list: dict[str, Any]
    prep_suggestions: list[dict[str, Any]]
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class MealPlanGenerationRequest(SQLModel):
    """Schema for meal plan generation request."""

    num_days: int = Field(ge=3, le=7)
    plan_style: str = Field(pattern="^(variety|simple_repeats)$")
    introduce_new_foods: bool = Field(default=False)


