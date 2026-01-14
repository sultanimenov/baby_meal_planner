"""Avoid list validation rule."""

from typing import Any


def check_avoid_list(
    plan_days: list[dict[str, Any]],
    avoid_list: list[str],
    food_items: dict[str, dict[str, Any]],
) -> tuple[bool, list[str]]:
    """Check if plan contains any foods on the avoid list.

    Args:
        plan_days: List of day objects with meals
        avoid_list: List of food names to avoid
        food_items: Dict mapping food_item_id to food item data

    Returns:
        Tuple of (is_valid, violations)
        - is_valid: True if no violations
        - violations: List of violation messages
    """
    violations = []
    avoid_set = {name.lower() for name in avoid_list}

    for day_idx, day in enumerate(plan_days, 1):
        for meal in day.get("meals", []):
            ingredients = meal.get("ingredients", [])
            for ingredient in ingredients:
                food_id = ingredient.get("food_item_id")
                if food_id and food_id in food_items:
                    food = food_items[food_id]
                    food_name = food.get("name", "").lower()
                    if food_name in avoid_set:
                        violations.append(
                            f"Day {day_idx}, {meal.get('slot', 'meal')}: "
                            f"{food.get('name')} is on the avoid list"
                        )

    return len(violations) == 0, violations


