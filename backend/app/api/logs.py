"""Meal and reaction log API endpoints."""

import uuid
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import current_user
from app.core.database import get_session
from app.models.user import User
from app.schemas.logs import (
    MealLogCreate,
    MealLogRead,
    ReactionLogCreate,
    ReactionLogRead,
    TodayMealSlot,
)
from app.services.log_service import LogService
from app.services.profile_service import ProfileService

router = APIRouter()


# ==================== MEAL LOGS ====================


@router.post("/meal", response_model=MealLogRead, status_code=status.HTTP_201_CREATED)
async def create_meal_log(
    log_data: MealLogCreate,
    user: Annotated[User, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> MealLogRead:
    """Log a meal outcome."""
    profile = await ProfileService.get_by_user_id(session, user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Baby profile not found. Please create a profile first.",
        )

    log = await LogService.create_meal_log(
        session=session,
        user_id=user.id,
        baby_profile_id=profile.id,
        log_date=log_data.date,
        meal_slot=log_data.meal_slot,
        outcome=log_data.outcome,
        recipe_id=log_data.recipe_id,
        meal_plan_id=log_data.meal_plan_id,
        notes=log_data.notes,
    )

    enriched = await LogService.enrich_meal_log_with_recipe(session, log)
    return MealLogRead(**enriched)


@router.get("/meal", response_model=list[MealLogRead])
async def list_meal_logs(
    user: Annotated[User, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    limit: int = Query(default=50, le=100),
) -> list[MealLogRead]:
    """Get meal logs with optional date filters."""
    profile = await ProfileService.get_by_user_id(session, user.id)
    if not profile:
        return []

    logs = await LogService.list_meal_logs(
        session=session,
        baby_profile_id=profile.id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )

    result = []
    for log in logs:
        enriched = await LogService.enrich_meal_log_with_recipe(session, log)
        result.append(MealLogRead(**enriched))

    return result


@router.get("/today", response_model=list[TodayMealSlot])
async def get_today_meals(
    user: Annotated[User, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
    for_date: date | None = Query(default=None, description="Date to get meals for (defaults to today)"),
) -> list[TodayMealSlot]:
    """Get today's meals with their log status.

    Returns meal slots from the active plan for the specified date,
    along with any existing logs for those slots.
    """
    profile = await ProfileService.get_by_user_id(session, user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Baby profile not found.",
        )

    target_date = for_date or date.today()

    # Get existing logs for this date
    logs = await LogService.get_meal_logs_for_date(
        session, profile.id, target_date
    )
    logs_by_slot = {log.meal_slot: log for log in logs}

    # Find active meal plan for this date
    from app.models.meal_plan import MealPlan
    from sqlalchemy import select

    result = await session.execute(
        select(MealPlan)
        .where(MealPlan.baby_profile_id == profile.id)
        .order_by(MealPlan.created_at.desc())
        .limit(1)
    )
    plan = result.scalar_one_or_none()

    slots: list[TodayMealSlot] = []

    if plan:
        # Find today's meals in the plan
        target_date_str = target_date.isoformat()
        for day in plan.days:
            if day.get("date") == target_date_str:
                for meal in day.get("meals", []):
                    slot_name = meal.get("slot")
                    recipe_id_str = meal.get("recipe_id")
                    recipe_id = uuid.UUID(recipe_id_str) if recipe_id_str else None

                    # Get recipe title if available
                    recipe_title = meal.get("recipe_title")
                    if not recipe_title and recipe_id:
                        recipe_title = await LogService.get_recipe_title(session, recipe_id)

                    # Check if we have a log for this slot
                    existing_log = logs_by_slot.get(slot_name)
                    log_read = None
                    if existing_log:
                        enriched = await LogService.enrich_meal_log_with_recipe(
                            session, existing_log
                        )
                        log_read = MealLogRead(**enriched)

                    slots.append(
                        TodayMealSlot(
                            date=target_date,
                            meal_slot=slot_name,
                            recipe_id=recipe_id,
                            recipe_title=recipe_title,
                            meal_plan_id=plan.id,
                            log=log_read,
                        )
                    )
                break

    # If no plan or date not in plan, return standard slots
    if not slots:
        # Return standard meal slots based on profile's meals_per_day
        standard_slots = ["breakfast", "lunch", "dinner"]
        if profile.meals_per_day >= 1:
            for slot_name in standard_slots[:profile.meals_per_day]:
                existing_log = logs_by_slot.get(slot_name)
                log_read = None
                if existing_log:
                    enriched = await LogService.enrich_meal_log_with_recipe(
                        session, existing_log
                    )
                    log_read = MealLogRead(**enriched)

                slots.append(
                    TodayMealSlot(
                        date=target_date,
                        meal_slot=slot_name,
                        recipe_id=None,
                        recipe_title=None,
                        meal_plan_id=None,
                        log=log_read,
                    )
                )

    return slots


# ==================== REACTION LOGS ====================


@router.post("/reaction", response_model=ReactionLogRead, status_code=status.HTTP_201_CREATED)
async def create_reaction_log(
    log_data: ReactionLogCreate,
    user: Annotated[User, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ReactionLogRead:
    """Log a suspected reaction."""
    profile = await ProfileService.get_by_user_id(session, user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Baby profile not found. Please create a profile first.",
        )

    log = await LogService.create_reaction_log(
        session=session,
        user_id=user.id,
        baby_profile_id=profile.id,
        symptoms=log_data.symptoms,
        severity=log_data.severity,
        occurred_at=log_data.occurred_at,
        suspected_food_ids=log_data.suspected_food_ids,
        suspected_recipe_ids=log_data.suspected_recipe_ids,
        notes=log_data.notes,
    )

    return ReactionLogRead.model_validate(log)


@router.get("/reaction", response_model=list[ReactionLogRead])
async def list_reaction_logs(
    user: Annotated[User, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
    limit: int = Query(default=50, le=100),
) -> list[ReactionLogRead]:
    """Get reaction logs."""
    profile = await ProfileService.get_by_user_id(session, user.id)
    if not profile:
        return []

    logs = await LogService.list_reaction_logs(
        session=session,
        baby_profile_id=profile.id,
        limit=limit,
    )

    return [ReactionLogRead.model_validate(log) for log in logs]


# ==================== FOOD HISTORY ====================


@router.get("/foods/introduced")
async def get_introduced_foods(
    user: Annotated[User, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
    sort_by: str = Query(
        default="date_introduced",
        pattern="^(name|date_introduced|preference_ratio)$",
    ),
) -> list[dict]:
    """Get list of introduced foods with preference stats.

    Returns all foods that have been tried, with counts of
    ate/partial/refused outcomes and a preference ratio.
    """
    profile = await ProfileService.get_by_user_id(session, user.id)
    if not profile:
        return []

    return await LogService.get_introduced_foods(
        session=session,
        baby_profile_id=profile.id,
        sort_by=sort_by,
    )


@router.get("/foods/summary")
async def get_food_preference_summary(
    user: Annotated[User, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict:
    """Get summary of food preferences.

    Returns counts and top favorite/refused foods.
    """
    profile = await ProfileService.get_by_user_id(session, user.id)
    if not profile:
        return {
            "total_foods_tried": 0,
            "favorite_foods": [],
            "refused_foods": [],
            "reaction_foods": [],
        }

    return await LogService.get_food_preference_summary(
        session=session,
        baby_profile_id=profile.id,
    )

