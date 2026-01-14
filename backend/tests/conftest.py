"""Pytest configuration and fixtures."""

import pytest


@pytest.fixture
def sample_food_items():
    """Sample food items for testing."""
    return {
        "honey-id": {
            "name": "Honey",
            "is_blocked_under_12m": True,
            "is_choking_hazard": False,
            "safe_form_notes": None,
        },
        "grape-id": {
            "name": "Grapes",
            "is_blocked_under_12m": False,
            "is_choking_hazard": True,
            "safe_form_notes": "Cut lengthwise into quarters",
        },
        "sweet-potato-id": {
            "name": "Sweet Potato",
            "is_blocked_under_12m": False,
            "is_choking_hazard": False,
            "safe_form_notes": None,
        },
        "peanut-id": {
            "name": "Peanut Butter",
            "is_blocked_under_12m": False,
            "is_choking_hazard": True,
            "safe_form_notes": "Thin layer only",
        },
    }


@pytest.fixture
def sample_plan_days():
    """Sample plan days for testing."""
    return [
        {
            "date": "2026-01-12",
            "meals": [
                {
                    "slot": "breakfast",
                    "recipe_id": "recipe-1",
                    "ingredients": [
                        {"food_item_id": "sweet-potato-id", "prep_notes": "mashed"}
                    ],
                },
                {
                    "slot": "lunch",
                    "recipe_id": "recipe-2",
                    "ingredients": [
                        {"food_item_id": "grape-id", "prep_notes": "cut"}
                    ],
                },
            ],
        }
    ]


