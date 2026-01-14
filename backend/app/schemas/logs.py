"""Pydantic schemas for meal and reaction logs."""

import uuid
from datetime import date, datetime

from pydantic import Field, field_validator
from sqlmodel import SQLModel


class MealLogCreate(SQLModel):
    """Schema for creating a meal log."""

    date: date
    meal_slot: str = Field(pattern="^(breakfast|lunch|dinner|snack)$")
    recipe_id: uuid.UUID | None = None
    meal_plan_id: uuid.UUID | None = None
    outcome: str = Field(pattern="^(ate|partial|refused)$")
    notes: str | None = None

    @field_validator("date")
    @classmethod
    def date_not_future(cls, v: date) -> date:
        """Validate date is not in the future."""
        if v > date.today():
            raise ValueError("Date cannot be in the future")
        return v


class MealLogRead(SQLModel):
    """Schema for reading a meal log."""

    id: uuid.UUID
    user_id: uuid.UUID
    baby_profile_id: uuid.UUID
    meal_plan_id: uuid.UUID | None
    date: date
    meal_slot: str
    recipe_id: uuid.UUID | None
    outcome: str
    notes: str | None
    recipe_title: str | None = None  # Populated from join
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class MealLogUpdate(SQLModel):
    """Schema for updating a meal log."""

    outcome: str | None = Field(default=None, pattern="^(ate|partial|refused)$")
    notes: str | None = None


class ReactionLogCreate(SQLModel):
    """Schema for creating a reaction log."""

    occurred_at: datetime | None = None  # Defaults to now if not provided
    symptoms: str = Field(min_length=1)
    severity: str = Field(default="mild", pattern="^(mild|moderate|severe)$")
    suspected_food_ids: list[uuid.UUID] = Field(default_factory=list)
    suspected_recipe_ids: list[uuid.UUID] = Field(default_factory=list)
    notes: str | None = None


class ReactionLogRead(SQLModel):
    """Schema for reading a reaction log."""

    id: uuid.UUID
    user_id: uuid.UUID
    baby_profile_id: uuid.UUID
    occurred_at: datetime
    symptoms: str
    severity: str
    suspected_food_ids: list[str]
    suspected_recipe_ids: list[str]
    suspected_food_names: list[str] = Field(default_factory=list)  # Populated from join
    suspected_recipe_titles: list[str] = Field(default_factory=list)  # Populated from join
    notes: str | None
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class TodayMealSlot(SQLModel):
    """Schema for a meal slot in the Today view."""

    date: date
    meal_slot: str
    recipe_id: uuid.UUID | None = None
    recipe_title: str | None = None
    meal_plan_id: uuid.UUID | None = None
    log: MealLogRead | None = None  # Existing log for this slot if any


