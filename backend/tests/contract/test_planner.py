"""Contract test for planner graph output schema."""

import uuid

import pytest
from pydantic import ValidationError

from app.planner.state import PlannerState
from app.schemas.llm_output import LLMDraftPlan


class TestPlannerGraphContract:
    """Contract tests to verify planner graph output schema.
    
    Note: PlannerState is a TypedDict (not Pydantic) for LangGraph compatibility.
    These tests verify the dict structure used in the graph.
    LLM output validation is done via LLMDraftPlan Pydantic model.
    """

    def test_planner_state_has_required_fields(self):
        """Test that PlannerState dict has all required fields for graph execution."""
        state: PlannerState = {
            "user_id": str(uuid.uuid4()),
            "baby_profile_id": str(uuid.uuid4()),
            "num_days": 7,
            "plan_style": "variety",
            "introduce_new_foods": False,
        }

        # Required input fields
        assert state["user_id"] is not None
        assert state["baby_profile_id"] is not None
        assert state["num_days"] in [3, 7]
        assert state["plan_style"] in ["variety", "simple_repeats"]

    def test_planner_state_accepts_valid_draft_plan(self):
        """Test that PlannerState accepts a valid draft plan structure."""
        state: PlannerState = {
            "user_id": str(uuid.uuid4()),
            "baby_profile_id": str(uuid.uuid4()),
            "num_days": 3,
            "plan_style": "variety",
            "draft_plan": {
                "days": [
                    {
                        "date": "2026-01-12",
                        "meals": [
                            {
                                "slot": "breakfast",
                                "recipe_id": str(uuid.uuid4()),
                                "is_new_food": False,
                                "new_food_items": [],
                                "notes": "",
                            }
                        ],
                    }
                ]
            },
        }

        assert state["draft_plan"] is not None
        assert "days" in state["draft_plan"]
        assert len(state["draft_plan"]["days"]) == 1

    def test_planner_state_accepts_shopping_list(self):
        """Test that PlannerState accepts shopping list structure."""
        state: PlannerState = {
            "user_id": str(uuid.uuid4()),
            "baby_profile_id": str(uuid.uuid4()),
            "num_days": 7,
            "plan_style": "variety",
            "shopping_list": {
                "produce": [
                    {"name": "Sweet Potato", "quantity": 2, "unit": "pieces", "meals": ["breakfast"]}
                ],
                "protein": [{"name": "Chicken", "quantity": 1, "unit": "lb", "meals": ["lunch"]}],
            },
        }

        assert isinstance(state["shopping_list"], dict)
        assert "produce" in state["shopping_list"]
        assert len(state["shopping_list"]["produce"]) > 0

    def test_planner_state_accepts_prep_suggestions(self):
        """Test that PlannerState accepts prep suggestions structure."""
        state: PlannerState = {
            "user_id": str(uuid.uuid4()),
            "baby_profile_id": str(uuid.uuid4()),
            "num_days": 7,
            "plan_style": "variety",
            "prep_suggestions": [
                {
                    "day": "Sunday",
                    "suggestion": "Prepare bulk items",
                    "items": ["Sweet Potato", "Carrot"],
                }
            ],
        }

        assert isinstance(state["prep_suggestions"], list)
        assert len(state["prep_suggestions"]) > 0
        assert "suggestion" in state["prep_suggestions"][0]

    def test_planner_state_num_days_values(self):
        """Test that num_days accepts valid values."""
        # Valid: 3 days
        state: PlannerState = {
            "user_id": str(uuid.uuid4()),
            "baby_profile_id": str(uuid.uuid4()),
            "num_days": 3,
            "plan_style": "variety",
        }
        assert state["num_days"] == 3

        # Valid: 7 days
        state: PlannerState = {
            "user_id": str(uuid.uuid4()),
            "baby_profile_id": str(uuid.uuid4()),
            "num_days": 7,
            "plan_style": "variety",
        }
        assert state["num_days"] == 7

    def test_planner_state_plan_style_values(self):
        """Test that plan_style accepts valid values."""
        # Valid: variety
        state: PlannerState = {
            "user_id": str(uuid.uuid4()),
            "baby_profile_id": str(uuid.uuid4()),
            "num_days": 7,
            "plan_style": "variety",
        }
        assert state["plan_style"] == "variety"

        # Valid: simple_repeats
        state: PlannerState = {
            "user_id": str(uuid.uuid4()),
            "baby_profile_id": str(uuid.uuid4()),
            "num_days": 7,
            "plan_style": "simple_repeats",
        }
        assert state["plan_style"] == "simple_repeats"


class TestLLMOutputValidation:
    """Contract tests for LLM output validation via Pydantic.
    
    Per constitution II.47: All LLM outputs MUST be structured (Pydantic)
    and validated before use.
    """

    def test_valid_draft_plan_passes_validation(self):
        """Test that a valid draft plan passes Pydantic validation."""
        raw_plan = {
            "days": [
                {
                    "date": "2026-01-14",
                    "meals": [
                        {
                            "slot": "breakfast",
                            "recipe": {
                                "title": "Baby Oatmeal",
                                "description": "Smooth oatmeal for babies",
                                "ingredients": [
                                    {"name": "oats", "quantity": 0.5, "unit": "cup"}
                                ],
                            },
                            "is_new_food": False,
                        }
                    ],
                }
            ]
        }
        
        plan = LLMDraftPlan.from_llm_response(raw_plan)
        assert len(plan.days) == 1
        assert plan.days[0].date == "2026-01-14"
        assert len(plan.days[0].meals) == 1
        assert plan.days[0].meals[0].slot == "breakfast"

    def test_invalid_date_format_fails_validation(self):
        """Test that invalid date format fails Pydantic validation."""
        raw_plan = {
            "days": [
                {
                    "date": "14-01-2026",  # Wrong format
                    "meals": [],
                }
            ]
        }
        
        with pytest.raises(ValidationError):
            LLMDraftPlan.from_llm_response(raw_plan)

    def test_missing_days_fails_validation(self):
        """Test that missing days array fails Pydantic validation."""
        raw_plan = {}
        
        with pytest.raises(ValidationError):
            LLMDraftPlan.from_llm_response(raw_plan)

    def test_empty_days_fails_validation(self):
        """Test that empty days array fails Pydantic validation."""
        raw_plan = {"days": []}
        
        with pytest.raises(ValidationError):
            LLMDraftPlan.from_llm_response(raw_plan)

    def test_meal_slot_normalized_to_lowercase(self):
        """Test that meal slots are normalized to lowercase."""
        raw_plan = {
            "days": [
                {
                    "date": "2026-01-14",
                    "meals": [
                        {
                            "slot": "BREAKFAST",  # Uppercase
                            "recipe": {"title": "Test"},
                        }
                    ],
                }
            ]
        }
        
        plan = LLMDraftPlan.from_llm_response(raw_plan)
        assert plan.days[0].meals[0].slot == "breakfast"

    def test_to_dict_conversion(self):
        """Test that validated plan can be converted to dict for state."""
        raw_plan = {
            "days": [
                {
                    "date": "2026-01-14",
                    "meals": [{"slot": "lunch", "recipe": {"title": "Soup"}}],
                }
            ]
        }
        
        plan = LLMDraftPlan.from_llm_response(raw_plan)
        plan_dict = plan.to_dict()
        
        assert isinstance(plan_dict, dict)
        assert "days" in plan_dict
        assert len(plan_dict["days"]) == 1
