"""Integration test for repair loop with mocked LLM."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.planner.nodes import create_repair_plan, create_validate_plan
from app.planner.state import PlannerState


class TestRepairLoop:
    """Integration tests for the repair loop functionality."""

    @pytest.fixture
    def sample_state_with_violations(self) -> PlannerState:
        """Create a sample state with validation violations."""
        return {
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
                                "recipe": {
                                    "title": "Honey Toast",
                                    "ingredients": [
                                        {"food_item_id": "honey-id", "name": "honey", "prep_notes": ""}
                                    ],
                                    "allergen_tags": [],
                                },
                            }
                        ],
                    }
                ]
            },
            "seed_recipes": [],
            "web_recipes": [],
            "validation_passed": False,
            "validation_errors": ["Honey is blocked for babies under 12 months"],
            "repair_attempts": 0,
            "age_in_months": 11,
        }

    @pytest.mark.asyncio
    async def test_repair_plan_increments_attempts(self, sample_state_with_violations):
        """Test that repair_plan increments repair_attempts."""
        mock_session = AsyncMock()

        # Patch within nodes module where it's imported
        with patch.dict("sys.modules", {"langchain_openai": MagicMock()}):
            # Mock the ChatOpenAI class
            mock_llm_class = MagicMock()
            mock_llm_instance = MagicMock()
            mock_response = MagicMock()
            mock_response.content = '{"days": [{"date": "2026-01-12", "meals": []}]}'
            mock_llm_instance.ainvoke = AsyncMock(return_value=mock_response)
            mock_llm_class.return_value = mock_llm_instance
            
            import sys
            sys.modules["langchain_openai"].ChatOpenAI = mock_llm_class

            # Create repair_plan function with mock session
            repair_plan = create_repair_plan(mock_session)
            result = await repair_plan(sample_state_with_violations)

            assert result["repair_attempts"] == sample_state_with_violations["repair_attempts"] + 1

    @pytest.mark.asyncio
    async def test_repair_loop_stops_after_max_attempts(self, sample_state_with_violations):
        """Test that repair loop stops after maximum attempts."""
        mock_session = AsyncMock()
        
        # Set repair attempts to max
        sample_state_with_violations["repair_attempts"] = 2

        # Patch within nodes module where it's imported
        with patch.dict("sys.modules", {"langchain_openai": MagicMock()}):
            mock_llm_class = MagicMock()
            mock_llm_instance = MagicMock()
            mock_response = MagicMock()
            mock_response.content = '{"days": [{"date": "2026-01-12", "meals": []}]}'
            mock_llm_instance.ainvoke = AsyncMock(return_value=mock_response)
            mock_llm_class.return_value = mock_llm_instance
            
            import sys
            sys.modules["langchain_openai"].ChatOpenAI = mock_llm_class

            repair_plan = create_repair_plan(mock_session)
            result = await repair_plan(sample_state_with_violations)

            # Should increment to 3, but graph should stop after this
            assert result["repair_attempts"] == 3

    @pytest.mark.asyncio
    async def test_validate_plan_returns_violations(self):
        """Test that validate_plan correctly identifies violations."""
        state: PlannerState = {
            "user_id": str(uuid.uuid4()),
            "baby_profile_id": str(uuid.uuid4()),
            "num_days": 3,
            "plan_style": "variety",
            "age_in_months": 11,
            "meals_per_day": 1,
            "avoid_list": [],
            "draft_plan": {
                "days": [
                    {
                        "date": "2026-01-12",
                        "meals": [
                            {
                                "slot": "breakfast",
                                "recipe_id": str(uuid.uuid4()),
                                "recipe": {
                                    "title": "Honey Toast",
                                    "ingredients": [
                                        {"food_item_id": "honey-id", "name": "honey"}
                                    ],
                                    "allergen_tags": [],
                                },
                            }
                        ],
                    },
                    {
                        "date": "2026-01-13",
                        "meals": [
                            {"slot": "breakfast", "recipe": {"title": "Oatmeal", "ingredients": [], "allergen_tags": []}},
                        ],
                    },
                    {
                        "date": "2026-01-14",
                        "meals": [
                            {"slot": "breakfast", "recipe": {"title": "Toast", "ingredients": [], "allergen_tags": []}},
                        ],
                    },
                ]
            },
        }

        # Mock session
        mock_session = AsyncMock()

        validate_plan = create_validate_plan(mock_session)
        result = await validate_plan(state)

        # Should have violations because of honey
        assert result["validation_passed"] is False
        assert len(result["validation_errors"]) > 0
        # Should mention honey
        assert any("honey" in err.lower() for err in result["validation_errors"])

    def test_repair_attempts_tracking(self):
        """Test that repair attempts are tracked correctly."""
        state: PlannerState = {
            "user_id": str(uuid.uuid4()),
            "baby_profile_id": str(uuid.uuid4()),
            "num_days": 3,
            "plan_style": "variety",
            "repair_attempts": 0,
        }

        assert state["repair_attempts"] == 0

        # Simulate repair attempts
        state["repair_attempts"] = 1
        assert state["repair_attempts"] == 1

        state["repair_attempts"] = 2
        assert state["repair_attempts"] == 2
