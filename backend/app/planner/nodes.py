"""LangGraph node implementations for meal plan generation."""

import logging
import uuid
from collections import defaultdict
from datetime import date, timedelta
from typing import Any, Callable

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.baby_profile import BabyProfile
from app.models.food_item import FoodItem
from app.models.logs import MealLog
from app.models.meal_plan import MealPlan
from app.models.recipe import Recipe
from app.planner.prompts import get_generate_draft_prompt, get_repair_prompt
from app.planner.search import search_recipes
from app.planner.state import PlannerState
from app.schemas.llm_output import LLMDraftPlan

# Logger for state transitions (per constitution II.56)
logger = logging.getLogger(__name__)

# Safety rules imported but using simplified inline checks for MVP
# from app.rules import check_avoid_list, check_choking_hazards, check_honey_under_12m, check_meal_slots_valid


def create_load_context(session: AsyncSession) -> Callable:
    """Create load_context node with bound session."""

    async def load_context(state: dict[str, Any]) -> dict[str, Any]:
        """Load baby profile context and compute derived values."""
        logger.info("STATE_TRANSITION: load_context started")
        
        baby_profile_id = state.get("baby_profile_id")
        if isinstance(baby_profile_id, str):
            baby_profile_id = uuid.UUID(baby_profile_id)

        # Load baby profile
        profile = await session.get(BabyProfile, baby_profile_id)
        if not profile:
            logger.error("STATE_TRANSITION: load_context failed - profile not found")
            raise ValueError(f"Baby profile {baby_profile_id} not found")

        # Compute age
        age_in_months = profile.age_in_months

        # Load history summary from meal logs
        history_summary = await _compute_history_summary(session, baby_profile_id)

        logger.info(
            "STATE_TRANSITION: load_context completed - "
            f"age={age_in_months}mo, feeding_style={profile.feeding_style}, "
            f"meals_per_day={profile.meals_per_day}"
        )

        return {
            "age_in_months": age_in_months,
            "feeding_style": profile.feeding_style,
            "meals_per_day": profile.meals_per_day,
            "dietary_preference": profile.dietary_preference,
            "allergens": profile.allergens or [],
            "avoid_list": profile.avoid_list or [],
            "max_prep_minutes": profile.max_prep_minutes,
            "history_summary": history_summary,
        }

    return load_context


def _normalize_draft_plan(draft_plan: dict[str, Any], start_date: date, num_days: int) -> dict[str, Any]:
    """Normalize draft plan dates and meal structure.
    
    - Fix dates to start from start_date
    - Extract recipe_title and recipe_id from recipe object
    - Ensure exactly num_days days
    """
    days = draft_plan.get("days", [])
    
    # Normalize dates and meal structure
    normalized_days = []
    for i in range(num_days):
        target_date = start_date + timedelta(days=i)
        target_date_str = target_date.isoformat()
        
        # Find or create day
        if i < len(days):
            day = days[i].copy()  # Copy to avoid mutating original
            # Update date to correct one
            day["date"] = target_date_str
        else:
            # Create empty day if missing
            day = {"date": target_date_str, "meals": []}
        
        # Normalize meals - extract recipe_title and recipe_id from recipe object
        normalized_meals = []
        for meal in day.get("meals", []):
            normalized_meal = meal.copy()
            
            # Extract recipe info if recipe object exists
            recipe = meal.get("recipe", {})
            if recipe:
                normalized_meal["recipe_id"] = recipe.get("id")
                normalized_meal["recipe_title"] = recipe.get("title")
                # Keep recipe object for full details
                normalized_meal["recipe"] = recipe
            else:
                # If no recipe object, try to get from existing fields
                if "recipe_id" not in normalized_meal:
                    normalized_meal["recipe_id"] = None
                if "recipe_title" not in normalized_meal:
                    normalized_meal["recipe_title"] = None
            
            normalized_meals.append(normalized_meal)
        
        day["meals"] = normalized_meals
        normalized_days.append(day)
    
    return {"days": normalized_days}


async def _compute_history_summary(
    session: AsyncSession, baby_profile_id: uuid.UUID
) -> dict[str, Any] | None:
    """Compute food preference summary from meal logs."""
    # Get meal logs from last 30 days
    cutoff_date = date.today() - timedelta(days=30)
    result = await session.execute(
        select(MealLog)
        .where(
            MealLog.baby_profile_id == baby_profile_id,
            MealLog.date >= cutoff_date,
            MealLog.recipe_id.isnot(None),
        )
    )
    logs = list(result.scalars().all())

    if not logs:
        return None

    # Get recipes and their ingredients
    recipe_ids = list(set(log.recipe_id for log in logs if log.recipe_id))
    recipes_result = await session.execute(
        select(Recipe).where(Recipe.id.in_(recipe_ids))
    )
    recipes_map = {r.id: r for r in recipes_result.scalars().all()}

    # Track food outcomes
    food_outcomes: dict[str, dict[str, int]] = defaultdict(lambda: {"ate": 0, "partial": 0, "refused": 0})

    for log in logs:
        recipe = recipes_map.get(log.recipe_id)
        if not recipe:
            continue

        # Extract food IDs from recipe ingredients
        for ingredient in recipe.ingredients:
            food_id = ingredient.get("food_item_id")
            if food_id:
                food_outcomes[food_id][log.outcome] += 1

    # Get food names
    food_ids = list(food_outcomes.keys())
    foods_result = await session.execute(
        select(FoodItem).where(FoodItem.id.in_([uuid.UUID(fid) for fid in food_ids]))
    )
    foods_map = {str(f.id): f.name for f in foods_result.scalars().all()}

    # Build summary
    liked_foods = []
    disliked_foods = []

    for food_id, outcomes in food_outcomes.items():
        total = outcomes["ate"] + outcomes["partial"] + outcomes["refused"]
        if total == 0:
            continue

        food_name = foods_map.get(food_id, food_id)
        like_ratio = (outcomes["ate"] + 0.5 * outcomes["partial"]) / total

        if like_ratio >= 0.7:
            liked_foods.append(food_name)
        elif like_ratio <= 0.3:
            disliked_foods.append(food_name)

    return {
        "liked_foods": liked_foods[:10],  # Top 10
        "disliked_foods": disliked_foods[:5],  # Top 5
        "total_meals_logged": len(logs),
    }


def create_retrieve_seeds(session: AsyncSession) -> Callable:
    """Create retrieve_seeds node with bound session."""

    async def retrieve_seeds(state: dict[str, Any]) -> dict[str, Any]:
        """Retrieve seed recipes from database filtered by profile."""
        logger.info("STATE_TRANSITION: retrieve_seeds started")
        
        # Build query filters
        query = select(Recipe)

        # Filter by age
        age_in_months = state.get("age_in_months")
        if age_in_months:
            query = query.where(Recipe.min_age_months <= age_in_months)

        # Filter by texture level if feeding style is puree or blw
        feeding_style = state.get("feeding_style")
        if feeding_style == "puree":
            query = query.where(Recipe.texture_level.in_(["puree", "soft_mash"]))
        elif feeding_style == "blw":
            query = query.where(Recipe.texture_level.in_(["finger_food", "soft_mash"]))

        # Filter by dietary preference
        dietary_preference = state.get("dietary_preference")
        if dietary_preference == "vegetarian":
            query = query.where(Recipe.is_vegetarian == True)

        # Filter by prep time
        max_prep_minutes = state.get("max_prep_minutes")
        if max_prep_minutes:
            query = query.where(Recipe.estimated_prep_minutes <= max_prep_minutes)

        # Execute query
        result = await session.execute(query)
        recipes = result.scalars().all()

        # Convert to dict format
        seed_recipes = []
        for recipe in recipes:
            recipe_dict = {
                "id": str(recipe.id),
                "title": recipe.title,
                "description": recipe.description,
                "texture_level": recipe.texture_level,
                "ingredients": recipe.ingredients,
                "steps": recipe.steps,
                "allergen_tags": recipe.allergen_tags,
                "estimated_prep_minutes": recipe.estimated_prep_minutes,
                "servings": recipe.servings,
                "min_age_months": recipe.min_age_months,
                "tags": recipe.tags,
                "cuisine_tags": recipe.cuisine_tags,
                "is_vegetarian": recipe.is_vegetarian,
                "safety_notes": recipe.safety_notes,
            }
            seed_recipes.append(recipe_dict)

        logger.info(f"STATE_TRANSITION: retrieve_seeds completed - found {len(seed_recipes)} recipes")

        return {"seed_recipes": seed_recipes}

    return retrieve_seeds


def create_search_recipes_node(session: AsyncSession) -> Callable:
    """Create search_recipes_node with bound session."""

    async def search_recipes_node(state: dict[str, Any]) -> dict[str, Any]:
        """Search for additional recipes from web sources."""
        # For MVP, we skip web search and just use seed recipes
        # This can be expanded later to include actual web search
        return {"web_recipes": []}

    return search_recipes_node


def create_generate_draft(session: AsyncSession) -> Callable:
    """Create generate_draft node with bound session."""

    async def generate_draft(state: dict[str, Any]) -> dict[str, Any]:
        """Generate draft meal plan using LLM."""
        import json
        from langchain_openai import ChatOpenAI

        logger.info("STATE_TRANSITION: generate_draft started")
        num_days = state.get("num_days", 3)

        # Combine recipes
        all_recipes = state.get("seed_recipes", []) + state.get("web_recipes", [])

        if not all_recipes:
            logger.error("STATE_TRANSITION: generate_draft failed - no recipes available")
            raise ValueError("No recipes available for plan generation")

        logger.info(f"STATE_TRANSITION: generate_draft - using {len(all_recipes)} recipes")

        # Get start date (today)
        start_date = date.today()
        
        # Generate prompt
        prompt = get_generate_draft_prompt(
            age_in_months=state.get("age_in_months", 6),
            feeding_style=state.get("feeding_style", "puree"),
            meals_per_day=state.get("meals_per_day", 2),
            num_days=num_days,
            plan_style=state.get("plan_style", "variety"),
            introduce_new_foods=state.get("introduce_new_foods", False),
            allergens=state.get("allergens", []),
            avoid_list=state.get("avoid_list", []),
            recipes=all_recipes,
            history_summary=state.get("history_summary"),
            start_date=start_date.isoformat(),
        )

        # Call LLM
        from app.core.config import settings
        llm = ChatOpenAI(
            model="gpt-4o-mini", 
            temperature=0.7,
            api_key=settings.openai_api_key,
        )
        
        logger.info("STATE_TRANSITION: generate_draft - calling LLM")
        response = await llm.ainvoke(prompt)

        # Parse response as JSON
        try:
            # Extract JSON from response
            content = response.content
            # Try to find JSON in the response
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                json_str = content.strip()

            raw_plan = json.loads(json_str)
        except (json.JSONDecodeError, IndexError) as e:
            logger.error(f"STATE_TRANSITION: generate_draft failed - JSON parse error: {e}")
            raise ValueError(f"Failed to parse LLM response as JSON: {e}")

        # Validate LLM output using Pydantic (per constitution II.47)
        try:
            validated_plan = LLMDraftPlan.from_llm_response(raw_plan)
            draft_plan = validated_plan.to_dict()
            logger.info(
                f"STATE_TRANSITION: generate_draft - LLM output validated, "
                f"got {len(draft_plan.get('days', []))} days"
            )
        except ValidationError as e:
            logger.error(f"STATE_TRANSITION: generate_draft - Pydantic validation failed: {e}")
            raise ValueError(f"LLM output failed schema validation: {e}")

        # Normalize dates and meal structure
        draft_plan = _normalize_draft_plan(draft_plan, start_date, num_days)
        
        logger.info("STATE_TRANSITION: generate_draft completed successfully")

        return {
            "draft_plan": draft_plan,
            "validation_passed": False,
            "validation_errors": [],
        }

    return generate_draft


def create_validate_plan(session: AsyncSession) -> Callable:
    """Create validate_plan node with bound session."""

    async def validate_plan(state: dict[str, Any]) -> dict[str, Any]:
        """Validate draft plan against safety rules."""
        repair_attempts = state.get("repair_attempts", 0)
        logger.info(f"STATE_TRANSITION: validate_plan started (attempt {repair_attempts + 1})")
        
        draft_plan = state.get("draft_plan", {})
        age_in_months = state.get("age_in_months", 6)
        avoid_list = state.get("avoid_list", [])
        meals_per_day = state.get("meals_per_day", 2)

        errors = []

        # Get all recipes referenced in the plan
        days = draft_plan.get("days", [])
        num_days = state.get("num_days", 3)
        
        if not days:
            errors.append("Plan has no days")
            logger.warning("STATE_TRANSITION: validate_plan failed - plan has no days")
            return {"validation_passed": False, "validation_errors": errors}
        
        # Check we have exactly num_days days
        if len(days) != num_days:
            errors.append(f"Plan must have exactly {num_days} days, but got {len(days)} days")

        for day_idx, day in enumerate(days, 1):
            meals = day.get("meals", [])

            # Check we have the right number of meals
            if len(meals) < meals_per_day:
                errors.append(f"Day {day_idx}: Expected {meals_per_day} meals, got {len(meals)}")

            for meal in meals:
                recipe = meal.get("recipe", {})
                if not recipe:
                    continue
                    
                ingredients = recipe.get("ingredients", [])
                allergen_tags = recipe.get("allergen_tags", [])

                # Check honey under 12 months (simple inline check)
                if age_in_months < 12:
                    for ing in ingredients:
                        name = ing.get("name", "").lower()
                        if "honey" in name:
                            errors.append(
                                f"Day {day_idx}, {meal.get('slot', 'meal')}: "
                                f"Honey is blocked for babies under 12 months"
                            )

                # Check avoid list
                for allergen in allergen_tags:
                    if allergen.lower() in [a.lower() for a in avoid_list]:
                        errors.append(
                            f"Day {day_idx}, {meal.get('slot', 'meal')}: "
                            f"Contains {allergen} which is on avoid list"
                        )

        validation_passed = len(errors) == 0

        if validation_passed:
            logger.info("STATE_TRANSITION: validate_plan passed - no violations found")
        else:
            logger.warning(
                f"STATE_TRANSITION: validate_plan failed - {len(errors)} violation(s): "
                f"{errors[:3]}{'...' if len(errors) > 3 else ''}"
            )

        return {
            "validation_passed": validation_passed,
            "validation_errors": errors,
        }

    return validate_plan


def create_repair_plan(session: AsyncSession) -> Callable:
    """Create repair_plan node with bound session."""

    async def repair_plan(state: dict[str, Any]) -> dict[str, Any]:
        """Repair plan to fix validation errors."""
        import json
        from langchain_openai import ChatOpenAI

        draft_plan = state.get("draft_plan", {})
        errors = state.get("validation_errors", [])
        repair_attempts = state.get("repair_attempts", 0)
        all_recipes = state.get("seed_recipes", []) + state.get("web_recipes", [])
        num_days = state.get("num_days", 3)
        start_date = date.today()

        logger.info(
            f"STATE_TRANSITION: repair_plan started (attempt {repair_attempts + 1}) - "
            f"fixing {len(errors)} error(s)"
        )

        # Generate repair prompt
        prompt = get_repair_prompt(
            draft_plan=draft_plan,
            errors=errors,
            recipes=all_recipes,
            start_date=start_date.isoformat(),
            num_days=num_days,
        )

        # Call LLM
        from app.core.config import settings
        llm = ChatOpenAI(
            model="gpt-4o-mini", 
            temperature=0.3,
            api_key=settings.openai_api_key,
        )
        response = await llm.ainvoke(prompt)

        # Parse response as JSON
        try:
            content = response.content
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                json_str = content.strip()

            raw_repaired = json.loads(json_str)
            
            # Validate repaired plan using Pydantic (per constitution II.47)
            try:
                validated_plan = LLMDraftPlan.from_llm_response(raw_repaired)
                repaired_plan = validated_plan.to_dict()
                logger.info("STATE_TRANSITION: repair_plan - LLM repair output validated")
            except ValidationError as ve:
                logger.warning(f"STATE_TRANSITION: repair_plan - validation failed: {ve}")
                repaired_plan = raw_repaired  # Use raw if validation fails
                
            # Normalize dates and meal structure after repair
            repaired_plan = _normalize_draft_plan(repaired_plan, start_date, num_days)
            logger.info("STATE_TRANSITION: repair_plan completed successfully")
        except (json.JSONDecodeError, IndexError) as e:
            # If repair fails, keep old plan
            logger.warning(f"STATE_TRANSITION: repair_plan failed to parse JSON: {e}")
            repaired_plan = draft_plan

        return {
            "draft_plan": repaired_plan,
            "repair_attempts": repair_attempts + 1,
        }

    return repair_plan


def create_derive_artifacts(session: AsyncSession) -> Callable:
    """Create derive_artifacts node with bound session."""

    async def derive_artifacts(state: dict[str, Any]) -> dict[str, Any]:
        """Derive shopping list and prep suggestions from plan."""
        logger.info("STATE_TRANSITION: derive_artifacts started")
        draft_plan = state.get("draft_plan", {})

        # Aggregate ingredients for shopping list
        ingredient_quantities: dict[str, dict] = {}
        days = draft_plan.get("days", [])

        for day in days:
            meals = day.get("meals", [])
            for meal in meals:
                recipe = meal.get("recipe", {})
                ingredients = recipe.get("ingredients", [])
                for ingredient in ingredients:
                    food_id = ingredient.get("food_item_id", "unknown")
                    name = ingredient.get("name", food_id)
                    quantity = ingredient.get("quantity", 1)
                    unit = ingredient.get("unit", "")

                    if name not in ingredient_quantities:
                        ingredient_quantities[name] = {
                            "name": name,
                            "total_quantity": 0,
                            "unit": unit,
                            "category": ingredient.get("category", "other"),
                        }
                    ingredient_quantities[name]["total_quantity"] += quantity

        # Build shopping list grouped by category
        shopping_list = {
            "items": list(ingredient_quantities.values()),
            "total_items": len(ingredient_quantities),
        }

        # Generate prep suggestions
        prep_suggestions = []
        unique_recipes = {}
        for day in days:
            for meal in day.get("meals", []):
                recipe = meal.get("recipe", {})
                title = recipe.get("title", "")
                if title and title not in unique_recipes:
                    unique_recipes[title] = recipe
                    prep_minutes = recipe.get("estimated_prep_minutes", 0)
                    if prep_minutes > 15:
                        prep_suggestions.append({
                            "recipe": title,
                            "suggestion": f"Consider prepping {title} in advance to save time.",
                            "time_saved_minutes": prep_minutes // 2,
                        })

        logger.info(
            f"STATE_TRANSITION: derive_artifacts completed - "
            f"{len(ingredient_quantities)} ingredients, {len(prep_suggestions)} prep suggestions"
        )

        return {
            "shopping_list": shopping_list,
            "prep_suggestions": prep_suggestions,
        }

    return derive_artifacts


def create_persist_plan(session: AsyncSession) -> Callable:
    """Create persist_plan node with bound session."""

    async def persist_plan(state: dict[str, Any]) -> dict[str, Any]:
        """Persist the validated meal plan to database."""
        logger.info("STATE_TRANSITION: persist_plan started")
        
        user_id = state.get("user_id")
        baby_profile_id = state.get("baby_profile_id")
        num_days = state.get("num_days", 3)
        plan_style = state.get("plan_style", "variety")
        introduce_new_foods = state.get("introduce_new_foods", False)
        draft_plan = state.get("draft_plan", {})
        shopping_list = state.get("shopping_list", {})
        prep_suggestions = state.get("prep_suggestions", [])

        # Convert UUIDs if needed
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
        if isinstance(baby_profile_id, str):
            baby_profile_id = uuid.UUID(baby_profile_id)

        # Create meal plan
        meal_plan = MealPlan(
            user_id=user_id,
            baby_profile_id=baby_profile_id,
            start_date=date.today(),
            num_days=num_days,
            plan_style=plan_style,
            introduce_new_foods=introduce_new_foods,
            days=draft_plan.get("days", []),
            shopping_list=shopping_list,
            prep_suggestions=prep_suggestions,
            generation_metadata={
                "seed_recipe_count": len(state.get("seed_recipes", [])),
                "web_recipe_count": len(state.get("web_recipes", [])),
                "validation_passed": state.get("validation_passed", False),
                "repair_attempts": state.get("repair_attempts", 0),
            },
        )

        session.add(meal_plan)
        await session.commit()
        await session.refresh(meal_plan)

        logger.info(
            f"STATE_TRANSITION: persist_plan completed - "
            f"plan_id={meal_plan.id}, num_days={num_days}, "
            f"repair_attempts={state.get('repair_attempts', 0)}"
        )

        return {"meal_plan_id": str(meal_plan.id)}

    return persist_plan
