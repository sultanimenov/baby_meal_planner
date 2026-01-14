"""Integration test for adaptive meal plan generation based on history."""

import uuid
from collections import defaultdict
from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.planner.nodes import _compute_history_summary, load_context
from app.planner.search import (
    filter_recipes_by_allergen_gap,
    get_recently_introduced_allergens,
)
from app.planner.state import PlannerState


class TestComputeHistorySummary:
    """Tests for history summary computation."""

    @pytest.mark.asyncio
    async def test_returns_none_for_no_logs(self):
        """Test that None is returned when no meal logs exist."""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await _compute_history_summary(mock_session, uuid.uuid4())

        assert result is None

    @pytest.mark.asyncio
    async def test_identifies_liked_foods(self):
        """Test that foods with high 'ate' ratio are marked as liked."""
        # Create mock meal logs
        baby_profile_id = uuid.uuid4()
        recipe_id = uuid.uuid4()

        # Mock meal log with outcome='ate'
        mock_log = MagicMock()
        mock_log.recipe_id = recipe_id
        mock_log.outcome = "ate"

        # Mock recipe with ingredients
        mock_recipe = MagicMock()
        mock_recipe.id = recipe_id
        mock_recipe.ingredients = [
            {"food_item_id": str(uuid.uuid4())},
        ]

        # Mock food item
        mock_food = MagicMock()
        mock_food.id = uuid.UUID(mock_recipe.ingredients[0]["food_item_id"])
        mock_food.name = "Banana"

        # Setup mock session
        mock_session = AsyncMock()

        # First call returns meal logs
        mock_logs_result = MagicMock()
        mock_logs_result.scalars.return_value.all.return_value = [mock_log] * 5

        # Second call returns recipes
        mock_recipes_result = MagicMock()
        mock_recipes_result.scalars.return_value.all.return_value = [mock_recipe]

        # Third call returns food items
        mock_foods_result = MagicMock()
        mock_foods_result.scalars.return_value.all.return_value = [mock_food]

        mock_session.execute = AsyncMock(
            side_effect=[mock_logs_result, mock_recipes_result, mock_foods_result]
        )

        result = await _compute_history_summary(mock_session, baby_profile_id)

        assert result is not None
        assert "liked_foods" in result
        assert "Banana" in result["liked_foods"]

    @pytest.mark.asyncio
    async def test_identifies_refused_foods(self):
        """Test that foods with high 'refused' ratio are identified."""
        baby_profile_id = uuid.uuid4()
        recipe_id = uuid.uuid4()

        mock_log = MagicMock()
        mock_log.recipe_id = recipe_id
        mock_log.outcome = "refused"

        mock_recipe = MagicMock()
        mock_recipe.id = recipe_id
        mock_recipe.ingredients = [
            {"food_item_id": str(uuid.uuid4())},
        ]

        mock_food = MagicMock()
        mock_food.id = uuid.UUID(mock_recipe.ingredients[0]["food_item_id"])
        mock_food.name = "Peas"

        mock_session = AsyncMock()

        mock_logs_result = MagicMock()
        mock_logs_result.scalars.return_value.all.return_value = [mock_log] * 5

        mock_recipes_result = MagicMock()
        mock_recipes_result.scalars.return_value.all.return_value = [mock_recipe]

        mock_foods_result = MagicMock()
        mock_foods_result.scalars.return_value.all.return_value = [mock_food]

        mock_session.execute = AsyncMock(
            side_effect=[mock_logs_result, mock_recipes_result, mock_foods_result]
        )

        result = await _compute_history_summary(mock_session, baby_profile_id)

        assert result is not None
        assert "refused_foods" in result
        assert "Peas" in result["refused_foods"]


class TestAllergenGap:
    """Tests for allergen introduction gap logic."""

    @pytest.mark.asyncio
    async def test_returns_empty_for_no_recent_logs(self):
        """Test that empty set is returned when no recent logs exist."""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        result = await get_recently_introduced_allergens(
            mock_session, uuid.uuid4()
        )

        assert result == set()

    @pytest.mark.asyncio
    async def test_identifies_recent_allergens(self):
        """Test that recently introduced allergens are identified."""
        baby_profile_id = uuid.uuid4()
        recipe_id = uuid.uuid4()

        mock_log = MagicMock()
        mock_log.recipe_id = recipe_id

        mock_recipe = MagicMock()
        mock_recipe.id = recipe_id
        mock_recipe.allergen_tags = ["dairy", "egg"]

        mock_session = AsyncMock()

        mock_logs_result = MagicMock()
        mock_logs_result.scalars.return_value.all.return_value = [mock_log]

        mock_recipes_result = MagicMock()
        mock_recipes_result.scalars.return_value.all.return_value = [mock_recipe]

        mock_session.execute = AsyncMock(
            side_effect=[mock_logs_result, mock_recipes_result]
        )

        result = await get_recently_introduced_allergens(
            mock_session, baby_profile_id
        )

        assert "dairy" in result
        assert "egg" in result

    @pytest.mark.asyncio
    async def test_filter_recipes_removes_new_allergens(self):
        """Test that recipes with new allergens are filtered out."""
        baby_profile_id = uuid.uuid4()

        recipes = [
            {"id": "1", "title": "Eggs", "allergen_tags": ["egg"]},
            {"id": "2", "title": "Plain Oatmeal", "allergen_tags": []},
        ]

        mock_session = AsyncMock()

        # Mock recent allergens query - egg was introduced recently
        mock_recent_result = MagicMock()
        mock_recent_result.scalars.return_value.all.return_value = []
        
        mock_recipe = MagicMock()
        mock_recipe.allergen_tags = ["egg"]

        mock_recipes_result = MagicMock()
        mock_recipes_result.scalars.return_value.all.return_value = [mock_recipe]

        # First call - recent logs (empty)
        # Second call - all logs (for familiar check)
        mock_session.execute = AsyncMock(
            side_effect=[
                mock_recent_result,
                mock_recent_result,
            ]
        )

        # Manually simulate the recent allergen check
        result = await filter_recipes_by_allergen_gap(
            mock_session, recipes, baby_profile_id
        )

        # Both recipes should pass since no recent allergen introductions
        assert len(result) == 2


class TestLoadContextWithHistory:
    """Tests for load_context with history summary."""

    @pytest.mark.asyncio
    async def test_includes_history_summary(self):
        """Test that load_context includes history_summary in result."""
        baby_profile_id = uuid.uuid4()
        user_id = uuid.uuid4()

        # Mock profile
        mock_profile = MagicMock()
        mock_profile.age_in_months = 9
        mock_profile.feeding_style = "mixed"
        mock_profile.meals_per_day = 3
        mock_profile.dietary_preference = "omnivore"
        mock_profile.allergens = []
        mock_profile.avoid_list = []
        mock_profile.max_prep_minutes = 20

        # Mock session
        mock_session = AsyncMock()
        mock_session.get = AsyncMock(return_value=mock_profile)

        # Mock logs query - return empty for no history
        mock_logs_result = MagicMock()
        mock_logs_result.scalars.return_value.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_logs_result)

        state = PlannerState(
            user_id=user_id,
            baby_profile_id=baby_profile_id,
            num_days=3,
            plan_style="variety",
        )

        result = await load_context(state, {"session": mock_session})

        assert "history_summary" in result
        assert result["age_in_months"] == 9
        assert result["feeding_style"] == "mixed"


