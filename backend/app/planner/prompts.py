"""LLM prompt templates for meal plan generation."""

from typing import Any


def get_generate_draft_prompt(
    age_in_months: int,
    feeding_style: str,
    meals_per_day: int,
    num_days: int,
    plan_style: str,
    introduce_new_foods: bool,
    allergens: list[str],
    avoid_list: list[str],
    recipes: list[dict[str, Any]],
    history_summary: dict[str, Any] | None = None,
    dietary_preference: str = "omnivore",
    max_prep_minutes: int = 30,
    start_date: str | None = None,
) -> str:
    """Generate prompt for creating draft meal plan."""
    age_text = f"{age_in_months} months old" if age_in_months else "unknown age"
    feeding_text = feeding_style or "mixed"
    meals_text = f"{meals_per_day} meal(s) per day" if meals_per_day else "2-3 meals"
    style_text = (
        "more variety" if plan_style == "variety" else "simple repeats with familiar foods"
    )

    history_text = ""
    if history_summary:
        liked = history_summary.get("liked_foods", [])
        refused = history_summary.get("disliked_foods", [])
        if liked or refused:
            history_text = "\n\nFood Preferences:\n"
            if liked:
                history_text += f"- Liked foods (include more often): {', '.join(liked[:10])}\n"
            if refused:
                history_text += f"- Refused foods (avoid or reduce): {', '.join(refused[:10])}\n"

    avoid_text = ""
    if avoid_list:
        avoid_text = f"\n\nAVOID these foods: {', '.join(avoid_list)}"

    allergen_text = ""
    if allergens:
        allergen_text = f"\n\nKnown allergens (do not introduce new ones): {', '.join(allergens)}"

    new_foods_text = ""
    if introduce_new_foods:
        new_foods_text = (
            "\n\nInclude 1-2 new foods per day and mark them with 'is_new_food: true'"
        )

    recipes_text = format_recipes_for_prompt(recipes)
    
    start_date_text = ""
    if start_date:
        start_date_text = f"\n\nIMPORTANT: The plan must start on {start_date}. Generate dates starting from {start_date} and increment by 1 day for each subsequent day."

    return f"""Generate a {num_days}-day meal plan for a baby who is {age_text}.

Baby Profile:
- Feeding style: {feeding_text}
- Target: {meals_text}
- Dietary preference: {dietary_preference}
- Max prep time per meal: {max_prep_minutes} minutes
- Plan style: {style_text}{history_text}{avoid_text}{allergen_text}{new_foods_text}

Available Recipes:
{recipes_text}

Requirements:
1. Create a plan with EXACTLY {num_days} days (no more, no less)
2. Each day must have exactly {meals_per_day} meal(s)
3. Meals should be age-appropriate and match the feeding style
4. Respect avoid list and allergen restrictions
5. Include variety while respecting plan style preference
6. All recipes must reference valid recipe IDs from the available recipes list
7. For each meal, include the COMPLETE recipe object with ALL details including:
   - id, title, description, texture_level
   - ingredients array with food_item_id, name, quantity, unit, category
   - steps array with order and instruction (cooking/preparation steps)
   - allergen_tags, estimated_prep_minutes, servings, tags, etc.
8. Include recipe steps (cooking instructions) in the recipe object{start_date_text}

Output format (JSON):
{{
  "days": [
    {{
      "date": "YYYY-MM-DD",
      "meals": [
        {{
          "slot": "breakfast|lunch|dinner|snack",
          "recipe": {{
            "id": "uuid",
            "title": "Recipe Title",
            "description": "Brief description",
            "texture_level": "puree|soft_mash|finger_food",
            "ingredients": [{{"food_item_id": "uuid", "name": "ingredient name", "quantity": 1, "unit": "tbsp", "category": "produce"}}],
            "steps": [{{"order": 1, "instruction": "Step-by-step cooking instruction"}}],
            "allergen_tags": [],
            "estimated_prep_minutes": 15,
            "servings": 1,
            "tags": ["breakfast"],
            "min_age_months": 6
          }},
          "is_new_food": false,
          "new_food_items": [],
          "notes": "optional notes"
        }}
      ]
    }}
  ]
}}
"""


def get_repair_prompt(
    draft_plan: dict[str, Any],
    errors: list[str],
    recipes: list[dict[str, Any]],
    start_date: str | None = None,
    num_days: int = 3,
) -> str:
    """Generate prompt for repairing validation violations."""
    import json
    
    violations_text = "\n".join(f"- {v}" for v in errors)
    plan_json = json.dumps(draft_plan, indent=2)
    
    start_date_text = ""
    if start_date:
        start_date_text = f"\n\nIMPORTANT: The plan must start on {start_date} and have exactly {num_days} days. Generate dates starting from {start_date} and increment by 1 day for each subsequent day."

    return f"""The meal plan failed validation. Please fix the following violations:

{violations_text}

Current plan:
{plan_json}

Available Recipes:
{format_recipes_for_prompt(recipes)}

Requirements:
- Make minimal changes to fix only the violations
- Keep everything else the same
- Ensure the plan has exactly {num_days} days
- Include complete recipe objects with all details (id, title, description, ingredients, steps, etc.)
- For each meal, include the full recipe object with steps array{start_date_text}

Output the corrected plan in the same JSON format.
"""


def format_recipes_for_prompt(recipes: list[dict]) -> str:
    """Format recipes list for prompt inclusion."""
    if not recipes:
        return "No recipes available."

    lines = []
    for recipe in recipes[:50]:  # Limit to 50 recipes
        recipe_id = recipe.get("id", "unknown")
        title = recipe.get("title", "Untitled")
        texture = recipe.get("texture_level", "unknown")
        tags = ", ".join(recipe.get("tags", []))
        prep_time = recipe.get("estimated_prep_minutes", 0)
        allergens = ", ".join(recipe.get("allergen_tags", [])) or "none"
        lines.append(f"- {recipe_id}: {title} ({texture}, prep: {prep_time}min, allergens: {allergens})")

    return "\n".join(lines)
