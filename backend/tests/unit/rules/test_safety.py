"""Unit tests for safety validation rules."""

import pytest

from app.rules.safety import check_choking_hazards, check_honey_under_12m


class TestHoneyUnder12m:
    """Tests for honey_under_12m rule."""

    def test_honey_blocked_for_11_month_old(self, sample_food_items):
        """Test that honey is blocked for 11-month-old."""
        plan_days = [
            {
                "date": "2026-01-12",
                "meals": [
                    {
                        "slot": "breakfast",
                        "recipe_id": "recipe-1",
                        "ingredients": [
                            {"food_item_id": "honey-id", "prep_notes": ""}
                        ],
                    }
                ],
            }
        ]

        is_valid, violations = check_honey_under_12m(plan_days, 11, sample_food_items)

        assert not is_valid
        assert len(violations) > 0
        assert "honey" in violations[0].lower() or "blocked" in violations[0].lower()

    def test_honey_allowed_for_12_month_old(self, sample_food_items):
        """Test that honey is allowed for 12-month-old."""
        plan_days = [
            {
                "date": "2026-01-12",
                "meals": [
                    {
                        "slot": "breakfast",
                        "recipe_id": "recipe-1",
                        "ingredients": [
                            {"food_item_id": "honey-id", "prep_notes": ""}
                        ],
                    }
                ],
            }
        ]

        is_valid, violations = check_honey_under_12m(plan_days, 12, sample_food_items)

        assert is_valid
        assert len(violations) == 0

    def test_no_honey_no_violations(self, sample_food_items):
        """Test that plan without honey passes validation."""
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

        is_valid, violations = check_honey_under_12m(plan_days, 11, sample_food_items)

        assert is_valid
        assert len(violations) == 0


class TestChokingHazards:
    """Tests for choking_hazards rule."""

    def test_choking_hazard_without_safe_notes_violates(self, sample_food_items):
        """Test that choking hazard without safe notes violates."""
        plan_days = [
            {
                "date": "2026-01-12",
                "meals": [
                    {
                        "slot": "breakfast",
                        "recipe_id": "recipe-1",
                        "ingredients": [
                            {
                                "food_item_id": "grape-id",
                                "prep_notes": None,  # No prep notes
                            }
                        ],
                    }
                ],
            }
        ]

        # Remove safe_form_notes from food item to test violation
        food_items_no_notes = sample_food_items.copy()
        food_items_no_notes["grape-id"] = {
            **food_items_no_notes["grape-id"],
            "safe_form_notes": None,
        }

        is_valid, violations = check_choking_hazards(
            plan_days, 6, food_items_no_notes
        )

        assert not is_valid
        assert len(violations) > 0
        assert "choking" in violations[0].lower()

    def test_choking_hazard_with_safe_notes_passes(self, sample_food_items):
        """Test that choking hazard with safe notes passes."""
        plan_days = [
            {
                "date": "2026-01-12",
                "meals": [
                    {
                        "slot": "breakfast",
                        "recipe_id": "recipe-1",
                        "ingredients": [
                            {
                                "food_item_id": "grape-id",
                                "prep_notes": "Cut into quarters",
                            }
                        ],
                    }
                ],
            }
        ]

        is_valid, violations = check_choking_hazards(plan_days, 6, sample_food_items)

        assert is_valid
        assert len(violations) == 0

    def test_non_choking_hazard_passes(self, sample_food_items):
        """Test that non-choking hazard passes regardless of notes."""
        plan_days = [
            {
                "date": "2026-01-12",
                "meals": [
                    {
                        "slot": "breakfast",
                        "recipe_id": "recipe-1",
                        "ingredients": [
                            {"food_item_id": "sweet-potato-id", "prep_notes": None}
                        ],
                    }
                ],
            }
        ]

        is_valid, violations = check_choking_hazards(plan_days, 6, sample_food_items)

        assert is_valid
        assert len(violations) == 0


