"""Pydantic schemas for baby profile."""

import uuid
from datetime import date, datetime

from pydantic import Field, field_validator
from sqlmodel import SQLModel


class BabyProfileBase(SQLModel):
    """Base schema for baby profile."""

    nickname: str = Field(min_length=1, max_length=100)
    date_of_birth: date
    feeding_style: str = Field(pattern="^(puree|blw|mixed)$")
    meals_per_day: int = Field(ge=1, le=3)
    dietary_preference: str = Field(default="omnivore", pattern="^(vegetarian|omnivore)$")
    cuisine_preferences: list[str] = Field(default_factory=list)
    allergens: list[str] = Field(default_factory=list)
    avoid_list: list[str] = Field(default_factory=list)
    max_prep_minutes: int = Field(default=30, ge=1)
    batch_cook_days: list[str] = Field(default_factory=list)
    pantry_staples: list[str] = Field(default_factory=list)

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, v: date) -> date:
        """Validate date of birth is within last 24 months."""
        from datetime import date, timedelta

        today = date.today()
        max_age = timedelta(days=730)  # ~24 months
        if v > today:
            raise ValueError("Date of birth cannot be in the future")
        if v < today - max_age:
            raise ValueError("Date of birth must be within last 24 months")
        return v


class BabyProfileCreate(BabyProfileBase):
    """Schema for creating a baby profile."""

    pass


class BabyProfileUpdate(SQLModel):
    """Schema for updating a baby profile."""

    nickname: str | None = Field(default=None, min_length=1, max_length=100)
    date_of_birth: date | None = None
    feeding_style: str | None = Field(default=None, pattern="^(puree|blw|mixed)$")
    meals_per_day: int | None = Field(default=None, ge=1, le=3)
    dietary_preference: str | None = Field(default=None, pattern="^(vegetarian|omnivore)$")
    cuisine_preferences: list[str] | None = None
    allergens: list[str] | None = None
    avoid_list: list[str] | None = None
    max_prep_minutes: int | None = Field(default=None, ge=1)
    batch_cook_days: list[str] | None = None
    pantry_staples: list[str] | None = None


class BabyProfileRead(BabyProfileBase):
    """Schema for reading a baby profile."""

    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    age_in_months: int

    class Config:
        """Pydantic config."""

        from_attributes = True


