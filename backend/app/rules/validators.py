"""Meal plan structure validators."""

from typing import Any


def check_meal_slots_valid(
    plan_days: list[dict[str, Any]], meals_per_day: int
) -> tuple[bool, list[str]]:
    """Check if meal slots match the target meals per day.

    Args:
        plan_days: List of day objects with meals
        meals_per_day: Target number of meals per day (1-3)

    Returns:
        Tuple of (is_valid, violations)
        - is_valid: True if all days have correct number of meals
        - violations: List of violation messages
    """
    violations = []

    for day_idx, day in enumerate(plan_days, 1):
        meals = day.get("meals", [])
        meal_count = len(meals)

        if meal_count != meals_per_day:
            violations.append(
                f"Day {day_idx}: Expected {meals_per_day} meal(s) per day, "
                f"but found {meal_count}"
            )

    return len(violations) == 0, violations


