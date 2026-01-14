"""Safety validation rules based on CDC guidelines."""

from typing import Any


def check_honey_under_12m(
    plan_days: list[dict[str, Any]], age_in_months: int, food_items: dict[str, dict[str, Any]]
) -> tuple[bool, list[str]]:
    """Check if plan contains honey for baby under 12 months.

    Args:
        plan_days: List of day objects with meals
        age_in_months: Baby's age in months
        food_items: Dict mapping food_item_id to food item data

    Returns:
        Tuple of (is_valid, violations)
        - is_valid: True if no violations
        - violations: List of violation messages
    """
    violations = []

    if age_in_months < 12:
        # Check all meals in all days
        for day_idx, day in enumerate(plan_days, 1):
            for meal in day.get("meals", []):
                recipe_id = meal.get("recipe_id")
                if not recipe_id:
                    continue

                # Check recipe ingredients for honey
                # Note: This assumes recipe data includes ingredient food_item_ids
                ingredients = meal.get("ingredients", [])
                for ingredient in ingredients:
                    food_id = ingredient.get("food_item_id")
                    if food_id and food_id in food_items:
                        food = food_items[food_id]
                        if food.get("name", "").lower() == "honey" or food.get(
                            "is_blocked_under_12m", False
                        ):
                            violations.append(
                                f"Day {day_idx}, {meal.get('slot', 'meal')}: "
                                f"Honey is blocked for babies under 12 months (CDC guidance)"
                            )

    return len(violations) == 0, violations


def check_choking_hazards(
    plan_days: list[dict[str, Any]], age_in_months: int, food_items: dict[str, dict[str, Any]]
) -> tuple[bool, list[str]]:
    """Check if plan contains choking hazards without safe preparation guidance.

    Args:
        plan_days: List of day objects with meals
        age_in_months: Baby's age in months
        food_items: Dict mapping food_item_id to food item data

    Returns:
        Tuple of (is_valid, violations)
        - is_valid: True if no violations or all hazards have safe_form_notes
        - violations: List of violation messages
    """
    violations = []

    for day_idx, day in enumerate(plan_days, 1):
        for meal in day.get("meals", []):
            ingredients = meal.get("ingredients", [])
            for ingredient in ingredients:
                food_id = ingredient.get("food_item_id")
                if food_id and food_id in food_items:
                    food = food_items[food_id]
                    if food.get("is_choking_hazard", False):
                        # Check if safe form notes are provided
                        safe_notes = food.get("safe_form_notes") or ingredient.get("prep_notes")
                        if not safe_notes:
                            violations.append(
                                f"Day {day_idx}, {meal.get('slot', 'meal')}: "
                                f"{food.get('name', 'Unknown')} is a choking hazard "
                                f"but no safe preparation guidance provided"
                            )

    return len(violations) == 0, violations


