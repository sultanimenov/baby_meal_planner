"""Unit tests for avoid_list validation rule."""

import pytest

from app.rules.avoid_list import check_avoid_list


class TestAvoidList:
    """Tests for avoid_list rule."""

    def test_food_on_avoid_list_violates(self, sample_food_items):
        """Test that food on avoid list violates."""
        plan_days = [
            {
                "date": "2026-01-12",
                "meals": [
                    {
                        "slot": "breakfast",
                        "recipe_id": "recipe-1",
                        "ingredients": [
                            {"food_item_id": "peanut-id", "prep_notes": ""}
                        ],
                    }
                ],
            }
        ]

        avoid_list = ["Peanut Butter", "peanuts"]

        is_valid, violations = check_avoid_list(plan_days, avoid_list, sample_food_items)

        assert not is_valid
        assert len(violations) > 0
        assert "peanut" in violations[0].lower() or "avoid" in violations[0].lower()

    def test_food_not_on_avoid_list_passes(self, sample_food_items):
        """Test that food not on avoid list passes."""
        plan_days = [
            {
                "date": "2026-01-12",
                "meals": [
                    {
                        "slot": "breakfast",
                        "recipe_id": "recipe-1",
                        "ingredients": [
                            {"food_item_id": "sweet-potato-id", "prep_notes": ""}
                        ],
                    }
                ],
            }
        ]

        avoid_list = ["Peanut Butter", "honey"]

        is_valid, violations = check_avoid_list(plan_days, avoid_list, sample_food_items)

        assert is_valid
        assert len(violations) == 0

    def test_case_insensitive_matching(self, sample_food_items):
        """Test that avoid list matching is case-insensitive."""
        plan_days = [
            {
                "date": "2026-01-12",
                "meals": [
                    {
                        "slot": "breakfast",
                        "recipe_id": "recipe-1",
                        "ingredients": [
                            {"food_item_id": "peanut-id", "prep_notes": ""}
                        ],
                    }
                ],
            }
        ]

        # Food name is "Peanut Butter", avoid list has "peanut butter" (lowercase)
        avoid_list = ["peanut butter"]

        is_valid, violations = check_avoid_list(plan_days, avoid_list, sample_food_items)

        assert not is_valid
        assert len(violations) > 0

    def test_empty_avoid_list_passes(self, sample_food_items):
        """Test that empty avoid list always passes."""
        plan_days = [
            {
                "date": "2026-01-12",
                "meals": [
                    {
                        "slot": "breakfast",
                        "recipe_id": "recipe-1",
                        "ingredients": [
                            {"food_item_id": "peanut-id", "prep_notes": ""}
                        ],
                    }
                ],
            }
        ]

        avoid_list = []

        is_valid, violations = check_avoid_list(plan_days, avoid_list, sample_food_items)

        assert is_valid
        assert len(violations) == 0


