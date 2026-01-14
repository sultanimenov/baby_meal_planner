"""Seed data loader for food items and recipes."""

import json
import uuid
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_maker
from app.models.food_item import FoodItem
from app.models.recipe import Recipe


async def load_foods(session: AsyncSession) -> dict[str, uuid.UUID]:
    """Load food items from seed file and return name->id mapping."""
    seed_dir = Path(__file__).parent.parent / "seed"
    foods_file = seed_dir / "foods.json"

    with open(foods_file) as f:
        foods_data = json.load(f)

    name_to_id: dict[str, uuid.UUID] = {}

    for food_data in foods_data:
        # Check if food already exists
        # Check if food item already exists by name
        from sqlalchemy import select
        result = await session.execute(
            select(FoodItem).where(FoodItem.name == food_data["name"])
        )
        existing = result.scalar_one_or_none()
        if existing:
            name_to_id[food_data["name"]] = existing.id
            continue

        # Create new food item
        food_item = FoodItem(**food_data)
        session.add(food_item)
        await session.flush()
        name_to_id[food_data["name"]] = food_item.id

    await session.commit()
    return name_to_id


async def load_recipes(session: AsyncSession, name_to_id: dict[str, uuid.UUID]) -> None:
    """Load recipes from seed file."""
    seed_dir = Path(__file__).parent.parent / "seed"
    recipes_file = seed_dir / "recipes.json"

    with open(recipes_file) as f:
        recipes_data = json.load(f)

    # Map food names to IDs in recipe ingredients
    name_mapping = {
        "sweet-potato": "Sweet Potato",
        "butternut-squash": "Butternut Squash",
        "whole-wheat-bread": "Whole Wheat Bread",
        "peanut-butter": "Peanut Butter",
        "almond-butter": "Almond Butter",
        "whole-nuts": "Whole Nuts",
        "cherry-tomatoes": "Cherry Tomatoes",
    }

    for recipe_data in recipes_data:
        # Check if recipe already exists by title
        result = await session.execute(
            select(Recipe).where(Recipe.title == recipe_data["title"])
        )
        existing = result.scalar_one_or_none()
        if existing:
            continue

        # Convert food item names to IDs in ingredients
        ingredients = []
        for ing in recipe_data["ingredients"]:
            food_name = ing.get("food_item_id", "")
            # Handle kebab-case names
            mapped_name = name_mapping.get(food_name, food_name)
            # Try to find the food item
            food_id = name_to_id.get(mapped_name)
            if not food_id:
                # Try case-insensitive lookup
                food_id = next(
                    (fid for name, fid in name_to_id.items() if name.lower() == mapped_name.lower()),
                    None,
                )
            if food_id:
                ing_copy = ing.copy()
                ing_copy["food_item_id"] = str(food_id)
                ingredients.append(ing_copy)

        recipe_data["ingredients"] = ingredients
        recipe = Recipe(**recipe_data)
        session.add(recipe)

    await session.commit()


async def seed_database() -> None:
    """Seed the database with food items and recipes."""
    async with async_session_maker() as session:
        print("Loading food items...")
        name_to_id = await load_foods(session)
        print(f"Loaded {len(name_to_id)} food items")

        print("Loading recipes...")
        await load_recipes(session, name_to_id)
        print("Recipes loaded successfully")


if __name__ == "__main__":
    import asyncio

    asyncio.run(seed_database())

