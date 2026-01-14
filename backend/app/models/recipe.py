"""Recipe model for curated recipes."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, Index, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class RecipeIngredient(SQLModel):
    """Recipe ingredient schema."""

    food_item_id: uuid.UUID
    quantity: float | None = None
    unit: str | None = None
    prep_notes: str | None = None


class RecipeStep(SQLModel):
    """Recipe step schema."""

    order: int
    instruction: str


class Recipe(SQLModel, table=True):
    """Recipe model for curated recipes with safety metadata."""

    __tablename__ = "recipes"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
    )
    title: str = Field(max_length=200)
    description: str | None = Field(default=None)
    texture_level: str = Field(max_length=20, index=True)  # puree, soft_mash, finger_food, mixed
    ingredients: list[dict[str, Any]] = Field(
        sa_column=Column(JSONB),
    )  # [{food_item_id, quantity, unit, prep_notes}]
    steps: list[dict[str, Any]] = Field(
        sa_column=Column(JSONB),
    )  # [{order, instruction}]
    allergen_tags: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSONB),
    )  # Derived from ingredients
    estimated_prep_minutes: int = Field(ge=1)
    servings: int = Field(default=1, ge=1)
    min_age_months: int = Field(default=6, ge=4, le=24)
    tags: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSONB),
    )  # breakfast, lunch, dinner, snack, etc.
    cuisine_tags: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSONB),
    )  # asian, mediterranean, etc.
    is_vegetarian: bool = Field(default=False, index=True)
    safety_notes: str | None = Field(default=None)
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

    # Add GIN indexes for JSONB fields
    __table_args__ = (
        Index("ix_recipes_allergen_tags", "allergen_tags", postgresql_using="gin"),
        Index("ix_recipes_tags", "tags", postgresql_using="gin"),
    )


