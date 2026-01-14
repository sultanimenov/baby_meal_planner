"""BabyProfile model."""

import uuid
from datetime import date, datetime
from typing import Any

from sqlalchemy import Column, DateTime, Index, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class BabyProfile(SQLModel, table=True):
    """Baby profile model - one per user for v1."""

    __tablename__ = "baby_profiles"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
    )
    user_id: uuid.UUID = Field(
        unique=True,
        index=True,
    )
    nickname: str = Field(max_length=100)
    date_of_birth: date
    feeding_style: str = Field(max_length=20)  # puree, blw, mixed
    meals_per_day: int = Field(ge=1, le=3)
    dietary_preference: str = Field(default="omnivore", max_length=20)  # vegetarian, omnivore
    cuisine_preferences: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSONB),
    )
    allergens: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSONB),
    )
    avoid_list: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSONB),
    )
    max_prep_minutes: int = Field(default=30, ge=1)
    batch_cook_days: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSONB),
    )
    pantry_staples: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSONB),
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
        ),
    )


    class Config:
        """Pydantic config."""

        arbitrary_types_allowed = True

    @property
    def age_in_months(self) -> int:
        """Calculate age in months from date of birth."""
        today = date.today()
        months = (today.year - self.date_of_birth.year) * 12 + (
            today.month - self.date_of_birth.month
        )
        if today.day < self.date_of_birth.day:
            months -= 1
        return max(0, months)

    # Table constraints
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_baby_profiles_user_id"),
        Index("ix_baby_profiles_user_id", "user_id"),
    )

