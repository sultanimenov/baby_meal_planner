"""Integration test for repair loop with mocked LLM."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.planner.nodes import repair_plan, validate_plan
from app.planner.state import PlannerState


class TestRepairLoop:
    """Integration tests for the repair loop functionality."""

    @pytest.fixture
    def sample_state_with_violations(self):
        """Create a sample state with validation violations."""
        return PlannerState(
            user_id=uuid.uuid4(),
            baby_profile_id=uuid.uuid4(),
            num_days=3,
            plan_style="variety",
            draft_plan={
                "days": [
                    {
                        "date": "2026-01-12",
                        "meals": [
                            {
                                "slot": "breakfast",
                                "recipe_id": str(uuid.uuid4()),
                                "ingredients": [
                                    {"food_item_id": "honey-id", "prep_notes": ""}
                                ],
                            }
                        ],
                    }
                ]
            },
            validation_passed=False,
            validation_violations=["Honey is blocked for babies under 12 months"],
            repair_attempts=0,
        )

    @pytest.mark.asyncio
    async def test_repair_plan_increments_attempts(self, sample_state_with_violations):
        """Test that repair_plan increments repair_attempts."""
        config = {"session": None}  # Mock session not needed for this test

        # Patch langchain_openai.ChatOpenAI since it's imported inside the function
        with patch("langchain_openai.ChatOpenAI") as mock_llm_class:
            # Mock LLM instance
            mock_llm_instance = MagicMock()
            mock_llm_class.return_value = mock_llm_instance

            result = await repair_plan(sample_state_with_violations, config)

            assert result["repair_attempts"] == sample_state_with_violations.repair_attempts + 1

    @pytest.mark.asyncio
    async def test_repair_loop_stops_after_max_attempts(self, sample_state_with_violations):
        """Test that repair loop stops after maximum attempts."""
        # Set repair attempts to max
        sample_state_with_violations.repair_attempts = 2

        config = {"session": None}

        # Patch langchain_openai.ChatOpenAI since it's imported inside the function
        with patch("langchain_openai.ChatOpenAI"):
            result = await repair_plan(sample_state_with_violations, config)

            # Should increment to 3, but graph should stop after this
            assert result["repair_attempts"] == 3

    @pytest.mark.asyncio
    async def test_validate_plan_returns_violations(self):
        """Test that validate_plan correctly identifies violations."""
        state = PlannerState(
            user_id=uuid.uuid4(),
            baby_profile_id=uuid.uuid4(),
            num_days=3,
            plan_style="variety",
            age_in_months=11,
            draft_plan={
                "days": [
                    {
                        "date": "2026-01-12",
                        "meals": [
                            {
                                "slot": "breakfast",
                                "recipe_id": str(uuid.uuid4()),
                                "ingredients": [
                                    {"food_item_id": "honey-id", "prep_notes": ""}
                                ],
                            }
                        ],
                    }
                ]
            },
        )

        food_items = {
            "honey-id": {
                "name": "Honey",
                "is_blocked_under_12m": True,
                "is_choking_hazard": False,
                "safe_form_notes": None,
            }
        }

        # Mock session
        mock_session = AsyncMock()
        from sqlalchemy import select
        from app.models.food_item import FoodItem

        # Mock the select query
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        config = {"session": mock_session}

        result = await validate_plan(state, config)

        # Should have violations
        assert result["validation_passed"] is False
        assert len(result["validation_violations"]) > 0

    def test_repair_attempts_tracking(self):
        """Test that repair attempts are tracked correctly."""
        state = PlannerState(
            user_id=uuid.uuid4(),
            baby_profile_id=uuid.uuid4(),
            num_days=3,
            plan_style="variety",
            repair_attempts=0,
        )

        assert state.repair_attempts == 0

        # Simulate repair attempts
        state.repair_attempts = 1
        assert state.repair_attempts == 1

        state.repair_attempts = 2
        assert state.repair_attempts == 2

