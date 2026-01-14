"""Service for meal and reaction log operations."""

import uuid
from collections import defaultdict
from datetime import date, datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.food_item import FoodItem
from app.models.logs import MealLog, ReactionLog
from app.models.recipe import Recipe


class LogService:
    """Service for managing meal and reaction logs."""

    # ==================== MEAL LOGS ====================

    @staticmethod
    async def create_meal_log(
        session: AsyncSession,
        user_id: uuid.UUID,
        baby_profile_id: uuid.UUID,
        log_date: date,
        meal_slot: str,
        outcome: str,
        recipe_id: uuid.UUID | None = None,
        meal_plan_id: uuid.UUID | None = None,
        notes: str | None = None,
    ) -> MealLog:
        """Create a new meal log.

        Args:
            session: Database session
            user_id: User ID
            baby_profile_id: Baby profile ID
            log_date: Date of the meal
            meal_slot: Meal slot (breakfast, lunch, dinner, snack)
            outcome: Outcome (ate, partial, refused)
            recipe_id: Optional recipe ID
            meal_plan_id: Optional meal plan ID
            notes: Optional notes

        Returns:
            Created MealLog
        """
        # Check for existing log for this slot/date
        existing = await LogService.get_meal_log_by_slot(
            session, baby_profile_id, log_date, meal_slot
        )
        if existing:
            # Update existing log instead of creating duplicate
            existing.outcome = outcome
            existing.notes = notes
            existing.recipe_id = recipe_id
            existing.meal_plan_id = meal_plan_id
            await session.commit()
            await session.refresh(existing)
            return existing

        log = MealLog(
            user_id=user_id,
            baby_profile_id=baby_profile_id,
            date=log_date,
            meal_slot=meal_slot,
            outcome=outcome,
            recipe_id=recipe_id,
            meal_plan_id=meal_plan_id,
            notes=notes,
        )
        session.add(log)
        await session.commit()
        await session.refresh(log)
        return log

    @staticmethod
    async def get_meal_log_by_slot(
        session: AsyncSession,
        baby_profile_id: uuid.UUID,
        log_date: date,
        meal_slot: str,
    ) -> MealLog | None:
        """Get meal log for a specific slot on a date.

        Args:
            session: Database session
            baby_profile_id: Baby profile ID
            log_date: Date
            meal_slot: Meal slot

        Returns:
            MealLog or None
        """
        result = await session.execute(
            select(MealLog).where(
                MealLog.baby_profile_id == baby_profile_id,
                MealLog.date == log_date,
                MealLog.meal_slot == meal_slot,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_meal_logs_for_date(
        session: AsyncSession,
        baby_profile_id: uuid.UUID,
        log_date: date,
    ) -> list[MealLog]:
        """Get all meal logs for a specific date.

        Args:
            session: Database session
            baby_profile_id: Baby profile ID
            log_date: Date

        Returns:
            List of MealLogs
        """
        result = await session.execute(
            select(MealLog)
            .where(
                MealLog.baby_profile_id == baby_profile_id,
                MealLog.date == log_date,
            )
            .order_by(MealLog.created_at)
        )
        return list(result.scalars().all())

    @staticmethod
    async def list_meal_logs(
        session: AsyncSession,
        baby_profile_id: uuid.UUID,
        start_date: date | None = None,
        end_date: date | None = None,
        limit: int = 50,
    ) -> list[MealLog]:
        """List meal logs for a baby profile.

        Args:
            session: Database session
            baby_profile_id: Baby profile ID
            start_date: Optional start date filter
            end_date: Optional end date filter
            limit: Maximum results

        Returns:
            List of MealLogs
        """
        query = select(MealLog).where(MealLog.baby_profile_id == baby_profile_id)

        if start_date:
            query = query.where(MealLog.date >= start_date)
        if end_date:
            query = query.where(MealLog.date <= end_date)

        query = query.order_by(MealLog.date.desc(), MealLog.created_at.desc()).limit(limit)

        result = await session.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_recipe_title(session: AsyncSession, recipe_id: uuid.UUID) -> str | None:
        """Get recipe title by ID.

        Args:
            session: Database session
            recipe_id: Recipe ID

        Returns:
            Recipe title or None
        """
        result = await session.execute(
            select(Recipe.title).where(Recipe.id == recipe_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def enrich_meal_log_with_recipe(
        session: AsyncSession, log: MealLog
    ) -> dict:
        """Enrich meal log with recipe title.

        Args:
            session: Database session
            log: MealLog

        Returns:
            Dict with log data and recipe_title
        """
        log_dict = {
            "id": log.id,
            "user_id": log.user_id,
            "baby_profile_id": log.baby_profile_id,
            "meal_plan_id": log.meal_plan_id,
            "date": log.date,
            "meal_slot": log.meal_slot,
            "recipe_id": log.recipe_id,
            "outcome": log.outcome,
            "notes": log.notes,
            "created_at": log.created_at,
            "recipe_title": None,
        }

        if log.recipe_id:
            log_dict["recipe_title"] = await LogService.get_recipe_title(
                session, log.recipe_id
            )

        return log_dict

    # ==================== REACTION LOGS ====================

    @staticmethod
    async def create_reaction_log(
        session: AsyncSession,
        user_id: uuid.UUID,
        baby_profile_id: uuid.UUID,
        symptoms: str,
        severity: str = "mild",
        occurred_at: datetime | None = None,
        suspected_food_ids: list[uuid.UUID] | None = None,
        suspected_recipe_ids: list[uuid.UUID] | None = None,
        notes: str | None = None,
    ) -> ReactionLog:
        """Create a new reaction log.

        Args:
            session: Database session
            user_id: User ID
            baby_profile_id: Baby profile ID
            symptoms: Symptom description
            severity: Severity level
            occurred_at: When reaction occurred
            suspected_food_ids: List of suspected food IDs
            suspected_recipe_ids: List of suspected recipe IDs
            notes: Optional notes

        Returns:
            Created ReactionLog
        """
        log = ReactionLog(
            user_id=user_id,
            baby_profile_id=baby_profile_id,
            symptoms=symptoms,
            severity=severity,
            occurred_at=occurred_at or datetime.utcnow(),
            suspected_food_ids=[str(fid) for fid in (suspected_food_ids or [])],
            suspected_recipe_ids=[str(rid) for rid in (suspected_recipe_ids or [])],
            notes=notes,
        )
        session.add(log)
        await session.commit()
        await session.refresh(log)
        return log

    @staticmethod
    async def list_reaction_logs(
        session: AsyncSession,
        baby_profile_id: uuid.UUID,
        limit: int = 50,
    ) -> list[ReactionLog]:
        """List reaction logs for a baby profile.

        Args:
            session: Database session
            baby_profile_id: Baby profile ID
            limit: Maximum results

        Returns:
            List of ReactionLogs
        """
        result = await session.execute(
            select(ReactionLog)
            .where(ReactionLog.baby_profile_id == baby_profile_id)
            .order_by(ReactionLog.occurred_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    # ==================== FOOD HISTORY ====================

    @staticmethod
    async def get_introduced_foods(
        session: AsyncSession,
        baby_profile_id: uuid.UUID,
        sort_by: str = "date_introduced",
    ) -> list[dict[str, Any]]:
        """Get list of introduced foods with preference stats.

        Args:
            session: Database session
            baby_profile_id: Baby profile ID
            sort_by: Sort field (name, date_introduced, preference_ratio)

        Returns:
            List of introduced food stats
        """
        # Get all meal logs with recipes
        logs = await session.execute(
            select(MealLog)
            .where(
                MealLog.baby_profile_id == baby_profile_id,
                MealLog.recipe_id.isnot(None),
            )
            .order_by(MealLog.date)
        )
        meal_logs = list(logs.scalars().all())

        if not meal_logs:
            return []

        # Get all recipes with their ingredients
        recipe_ids = list(set(log.recipe_id for log in meal_logs if log.recipe_id))
        recipes = await session.execute(
            select(Recipe).where(Recipe.id.in_(recipe_ids))
        )
        recipes_map = {r.id: r for r in recipes.scalars().all()}

        # Get all food items
        food_result = await session.execute(select(FoodItem))
        foods_map = {f.id: f for f in food_result.scalars().all()}

        # Track food stats
        food_stats: dict[uuid.UUID, dict[str, Any]] = defaultdict(
            lambda: {
                "ate_count": 0,
                "partial_count": 0,
                "refused_count": 0,
                "first_introduced": None,
            }
        )

        # Get reactions for has_reaction flag
        reactions = await session.execute(
            select(ReactionLog.suspected_food_ids)
            .where(ReactionLog.baby_profile_id == baby_profile_id)
        )
        reaction_food_ids: set[str] = set()
        for (food_ids,) in reactions:
            if food_ids:
                reaction_food_ids.update(food_ids)

        # Process logs to extract food stats
        for log in meal_logs:
            recipe = recipes_map.get(log.recipe_id)
            if not recipe or not recipe.ingredients:
                continue

            for ingredient in recipe.ingredients:
                food_id_str = ingredient.get("food_item_id")
                if not food_id_str:
                    continue

                try:
                    food_id = uuid.UUID(food_id_str)
                except (ValueError, TypeError):
                    continue

                stats = food_stats[food_id]

                # Update counts
                if log.outcome == "ate":
                    stats["ate_count"] += 1
                elif log.outcome == "partial":
                    stats["partial_count"] += 1
                elif log.outcome == "refused":
                    stats["refused_count"] += 1

                # Track first introduction
                if stats["first_introduced"] is None or log.date < stats["first_introduced"]:
                    stats["first_introduced"] = log.date

        # Build result list
        result = []
        for food_id, stats in food_stats.items():
            food = foods_map.get(food_id)
            if not food:
                continue

            total = stats["ate_count"] + stats["partial_count"] + stats["refused_count"]
            preference_ratio = stats["ate_count"] / total if total > 0 else 0.0

            result.append({
                "food_item_id": str(food_id),
                "name": food.name,
                "category": food.category,
                "first_introduced": stats["first_introduced"].isoformat() if stats["first_introduced"] else None,
                "ate_count": stats["ate_count"],
                "partial_count": stats["partial_count"],
                "refused_count": stats["refused_count"],
                "preference_ratio": round(preference_ratio, 2),
                "has_reaction": str(food_id) in reaction_food_ids,
            })

        # Sort results
        if sort_by == "name":
            result.sort(key=lambda x: x["name"].lower())
        elif sort_by == "preference_ratio":
            result.sort(key=lambda x: x["preference_ratio"], reverse=True)
        else:  # date_introduced
            result.sort(
                key=lambda x: x["first_introduced"] or "",
                reverse=True,
            )

        return result

    @staticmethod
    async def get_food_preference_summary(
        session: AsyncSession,
        baby_profile_id: uuid.UUID,
    ) -> dict[str, Any]:
        """Get summary of food preferences.

        Args:
            session: Database session
            baby_profile_id: Baby profile ID

        Returns:
            Summary dict with counts and top foods
        """
        foods = await LogService.get_introduced_foods(
            session, baby_profile_id, sort_by="preference_ratio"
        )

        if not foods:
            return {
                "total_foods_tried": 0,
                "favorite_foods": [],
                "refused_foods": [],
                "reaction_foods": [],
            }

        return {
            "total_foods_tried": len(foods),
            "favorite_foods": [f["name"] for f in foods[:5] if f["preference_ratio"] >= 0.7],
            "refused_foods": [f["name"] for f in foods if f["preference_ratio"] <= 0.3][:5],
            "reaction_foods": [f["name"] for f in foods if f["has_reaction"]],
        }

