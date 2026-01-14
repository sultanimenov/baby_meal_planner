"""Web search module for finding credible recipe sources."""

import uuid
from datetime import date, timedelta
from typing import Any

import httpx
from bs4 import BeautifulSoup
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.logs import MealLog
from app.models.recipe import Recipe


CREDIBLE_SOURCES = [
    "solidstarts.com",
    "babyledweaning.com",
    "feedinglittles.com",
    "healthychildren.org",
    "nhs.uk/start-for-life",
]

# Common allergens that require introduction gaps (3-5 days recommended)
COMMON_ALLERGENS = [
    "dairy",
    "egg",
    "peanut",
    "tree_nut",
    "wheat",
    "soy",
    "fish",
    "shellfish",
    "sesame",
]

# Recommended gap in days between introducing new allergens
ALLERGEN_INTRODUCTION_GAP_DAYS = 3


async def search_recipes(
    query: str, age_months: int, feeding_style: str, limit: int = 10
) -> list[dict[str, Any]]:
    """Search for recipes from credible sources.

    Args:
        query: Search query (e.g., "baby food recipes 6 months")
        age_months: Baby's age in months
        feeding_style: Feeding style (puree, blw, mixed)
        limit: Maximum number of results

    Returns:
        List of recipe dictionaries with title, description, source, etc.
    """
    # Placeholder implementation
    # In production, this would:
    # 1. Use a search API (Google Custom Search, Bing, etc.)
    # 2. Filter results to only credible sources
    # 3. Scrape recipe pages (respecting robots.txt)
    # 4. Extract structured recipe data
    # 5. Validate against safety rules

    # For now, return empty list - seed recipes will be used
    return []


async def get_recently_introduced_allergens(
    session: AsyncSession,
    baby_profile_id: uuid.UUID,
    days: int = ALLERGEN_INTRODUCTION_GAP_DAYS,
) -> set[str]:
    """Get allergens that were recently introduced (within gap period).

    Args:
        session: Database session
        baby_profile_id: Baby profile ID
        days: Number of days to look back

    Returns:
        Set of allergen tags introduced recently
    """
    cutoff_date = date.today() - timedelta(days=days)

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
        return set()

    # Get recipes
    recipe_ids = list(set(log.recipe_id for log in logs if log.recipe_id))
    recipes_result = await session.execute(
        select(Recipe).where(Recipe.id.in_(recipe_ids))
    )
    recipes = list(recipes_result.scalars().all())

    # Collect allergen tags
    recent_allergens: set[str] = set()
    for recipe in recipes:
        if recipe.allergen_tags:
            for tag in recipe.allergen_tags:
                if tag.lower() in [a.lower() for a in COMMON_ALLERGENS]:
                    recent_allergens.add(tag.lower())

    return recent_allergens


async def filter_recipes_by_allergen_gap(
    session: AsyncSession,
    recipes: list[dict[str, Any]],
    baby_profile_id: uuid.UUID,
    allow_familiar_allergens: bool = True,
) -> list[dict[str, Any]]:
    """Filter recipes to respect allergen introduction gaps.

    Only filters if recipe would introduce a NEW allergen. Recipes containing
    allergens already introduced are allowed.

    Args:
        session: Database session
        recipes: List of recipe dicts
        baby_profile_id: Baby profile ID
        allow_familiar_allergens: If True, allow allergens already eaten before

    Returns:
        Filtered list of recipes safe to use
    """
    if not recipes:
        return recipes

    # Get recently introduced allergens
    recent_allergens = await get_recently_introduced_allergens(
        session, baby_profile_id
    )

    if not recent_allergens:
        return recipes  # No recent allergen introductions, all recipes OK

    # Get all allergens ever introduced (for familiar check)
    familiar_allergens: set[str] = set()
    if allow_familiar_allergens:
        all_logs = await session.execute(
            select(MealLog)
            .where(
                MealLog.baby_profile_id == baby_profile_id,
                MealLog.recipe_id.isnot(None),
            )
        )
        all_log_list = list(all_logs.scalars().all())

        if all_log_list:
            recipe_ids = list(set(log.recipe_id for log in all_log_list if log.recipe_id))
            recipes_result = await session.execute(
                select(Recipe).where(Recipe.id.in_(recipe_ids))
            )
            for recipe in recipes_result.scalars().all():
                if recipe.allergen_tags:
                    familiar_allergens.update(
                        tag.lower() for tag in recipe.allergen_tags
                    )

    # Filter recipes
    safe_recipes = []
    for recipe in recipes:
        recipe_allergens = set(
            tag.lower() for tag in recipe.get("allergen_tags", [])
        )

        # Check if this recipe introduces new allergens from recent ones
        new_allergens = recipe_allergens - familiar_allergens

        # If recipe has new allergens AND any match recent introductions, skip
        if new_allergens and new_allergens & recent_allergens:
            continue

        safe_recipes.append(recipe)

    return safe_recipes


async def fetch_recipe_from_url(url: str) -> dict[str, Any] | None:
    """Fetch and parse a recipe from a URL.

    Args:
        url: Recipe URL

    Returns:
        Recipe dictionary or None if fetch/parse fails
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")
            # Extract recipe data from HTML
            # This is a placeholder - actual implementation would parse specific site formats

            return None
    except Exception:
        return None

