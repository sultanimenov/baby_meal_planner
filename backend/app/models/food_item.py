"""FoodItem model for reference data."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, Index, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class FoodItem(SQLModel, table=True):
    """FoodItem model for reference data with safety metadata."""

    __tablename__ = "food_items"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
    )
    name: str = Field(unique=True, index=True, max_length=100)
    category: str = Field(max_length=50, index=True)  # produce, protein, grain, dairy, etc.
    allergen_tags: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSONB),
    )  # dairy, egg, peanut, tree_nut, wheat, soy, fish, shellfish
    texture_suitability: dict[str, bool] = Field(
        default_factory=dict,
        sa_column=Column(JSONB),
    )  # {puree: true, blw: false, mixed: true}
    min_age_months: int = Field(default=6, ge=4, le=24)
    is_choking_hazard: bool = Field(default=False)
    safe_form_notes: str | None = Field(default=None)
    is_blocked_under_12m: bool = Field(default=False, index=True)
    blocked_reason: str | None = Field(default=None)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )

    class Config:
        """Pydantic config."""

        arbitrary_types_allowed = True


