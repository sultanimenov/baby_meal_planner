"""PlannerState model for LangGraph state machine."""

import uuid
from datetime import date
from typing import Any, TypedDict


class PlannerState(TypedDict, total=False):
    """State model for meal plan generation graph.
    
    Using TypedDict for LangGraph compatibility.
    """

    # Input
    user_id: str
    baby_profile_id: str
    num_days: int  # 3 or 7
    plan_style: str  # variety or simple_repeats
    introduce_new_foods: bool

    # Context (loaded in load_context)
    age_in_months: int
    feeding_style: str
    meals_per_day: int
    dietary_preference: str
    allergens: list[str]
    avoid_list: list[str]
    max_prep_minutes: int
    batch_cook_days: list[str]
    history_summary: dict[str, Any]

    # Seed recipes (loaded in retrieve_seeds)
    seed_recipes: list[dict[str, Any]]

    # Web search results (loaded in search_recipes)
    web_recipes: list[dict[str, Any]]

    # Draft plan (generated in generate_draft)
    draft_plan: dict[str, Any]

    # Validation results (from validate_plan)
    validation_passed: bool
    validation_errors: list[str]
    repair_attempts: int

    # Final artifacts (derived in derive_artifacts)
    shopping_list: dict[str, Any]
    prep_suggestions: list[dict[str, Any]]

    # Output (persisted in persist_plan)
    meal_plan_id: str
    start_date: str

    # Metadata
    generation_metadata: dict[str, Any]
