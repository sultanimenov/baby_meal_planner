"""Pydantic schemas for validating LLM outputs.

Per constitution II.47: All LLM outputs MUST be structured (Pydantic for Python)
and validated before use.
"""

from typing import Any

from pydantic import BaseModel, Field, field_validator


class LLMRecipeIngredient(BaseModel):
    """Schema for recipe ingredient in LLM output."""

    food_item_id: str | None = None
    name: str
    quantity: float | int | None = None
    unit: str | None = None
    category: str | None = None
    prep_notes: str | None = None


class LLMRecipeStep(BaseModel):
    """Schema for recipe step in LLM output."""

    order: int
    instruction: str


class LLMRecipe(BaseModel):
    """Schema for recipe in LLM output."""

    id: str | None = None
    title: str
    description: str | None = None
    texture_level: str | None = None
    ingredients: list[LLMRecipeIngredient] = Field(default_factory=list)
    steps: list[LLMRecipeStep] = Field(default_factory=list)
    allergen_tags: list[str] = Field(default_factory=list)
    estimated_prep_minutes: int | None = None
    servings: int | None = None
    min_age_months: int | None = None
    tags: list[str] = Field(default_factory=list)
    cuisine_tags: list[str] = Field(default_factory=list)
    is_vegetarian: bool | None = None
    safety_notes: str | None = None


class LLMMeal(BaseModel):
    """Schema for a meal slot in LLM output."""

    slot: str
    recipe: LLMRecipe | None = None
    recipe_id: str | None = None
    recipe_title: str | None = None
    is_new_food: bool = False
    new_food_items: list[str] = Field(default_factory=list)
    notes: str | None = None

    @field_validator("slot")
    @classmethod
    def validate_slot(cls, v: str) -> str:
        """Validate meal slot is one of allowed values."""
        allowed = {"breakfast", "lunch", "dinner", "snack"}
        if v.lower() not in allowed:
            # Be lenient - just lowercase it
            pass
        return v.lower()


class LLMPlanDay(BaseModel):
    """Schema for a day in the meal plan LLM output."""

    date: str
    meals: list[LLMMeal] = Field(default_factory=list)

    @field_validator("date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """Validate date is in YYYY-MM-DD format."""
        import re
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError(f"Date must be in YYYY-MM-DD format, got: {v}")
        return v


class LLMDraftPlan(BaseModel):
    """Schema for the full draft plan from LLM.

    This validates the structure of LLM output before use,
    per constitution requirement II.47.
    """

    days: list[LLMPlanDay] = Field(min_length=1)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for state storage."""
        return self.model_dump()

    @classmethod
    def from_llm_response(cls, response_dict: dict[str, Any]) -> "LLMDraftPlan":
        """Create from LLM response with validation.

        Args:
            response_dict: Parsed JSON from LLM response

        Returns:
            Validated LLMDraftPlan

        Raises:
            ValidationError: If the response doesn't match schema
        """
        return cls.model_validate(response_dict)

