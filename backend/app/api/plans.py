"""Meal plan API endpoints."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import current_user
from app.core.database import get_session
from app.models.user import User
from app.schemas.plan import MealPlanCreate, MealPlanRead
from app.services.plan_service import PlanService
from app.services.profile_service import ProfileService

router = APIRouter()


@router.post("", response_model=MealPlanRead, status_code=status.HTTP_201_CREATED)
async def create_plan(
    plan_data: MealPlanCreate,
    user: Annotated[User, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> MealPlanRead:
    """Generate a new meal plan."""
    # Get user's baby profile
    from app.models.baby_profile import BabyProfile
    from app.services.profile_service import ProfileService

    profile = await ProfileService.get_by_user_id(session, user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Baby profile not found. Please create a profile first.",
        )

    try:
        plan = await PlanService.generate_plan(
            session=session,
            user_id=user.id,
            baby_profile_id=profile.id,
            num_days=plan_data.num_days,
            plan_style=plan_data.plan_style,
            introduce_new_foods=plan_data.introduce_new_foods,
        )
        return MealPlanRead.model_validate(plan)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate plan: {str(e)}",
        )


@router.get("/{plan_id}", response_model=MealPlanRead)
async def get_plan(
    plan_id: uuid.UUID,
    user: Annotated[User, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> MealPlanRead:
    """Get a meal plan by ID."""
    plan = await PlanService.get_by_id(session, plan_id, user.id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found",
        )
    return MealPlanRead.model_validate(plan)


@router.get("", response_model=list[MealPlanRead])
async def list_plans(
    user: Annotated[User, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
    limit: int = 10,
) -> list[MealPlanRead]:
    """List meal plans for the current user."""
    plans = await PlanService.list_by_user(session, user.id, limit=limit)
    return [MealPlanRead.model_validate(plan) for plan in plans]


@router.patch("/{plan_id}/swap-meal", response_model=MealPlanRead)
async def swap_meal(
    plan_id: uuid.UUID,
    day_date: Annotated[str, Query()],
    meal_slot: Annotated[str, Query()],
    new_recipe_id: Annotated[uuid.UUID, Query()],
    user: Annotated[User, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> MealPlanRead:
    """Swap a meal in an existing plan."""
    plan = await PlanService.get_by_id(session, plan_id, user.id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found",
        )

    # Find and update the meal
    updated = False
    for day in plan.days:
        if day.get("date") == day_date:
            for meal in day.get("meals", []):
                if meal.get("slot") == meal_slot:
                    meal["recipe_id"] = str(new_recipe_id)
                    # Clear new_food flags since this is a manual swap
                    meal["is_new_food"] = False
                    meal["new_food_items"] = []
                    updated = True
                    break
            if updated:
                break

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Meal not found in plan",
        )

    # Recalculate shopping list
    from app.planner.nodes import derive_artifacts
    from app.planner.state import PlannerState

    # Create temporary state for shopping list recalculation
    temp_state = PlannerState(
        user_id=plan.user_id,
        baby_profile_id=plan.baby_profile_id,
        num_days=plan.num_days,
        plan_style=plan.plan_style,
        introduce_new_foods=plan.introduce_new_foods,
        draft_plan={"days": plan.days},
    )

    artifacts = await derive_artifacts(temp_state, {"session": session})
    plan.shopping_list = artifacts["shopping_list"]
    plan.prep_suggestions = artifacts["prep_suggestions"]

    await session.commit()
    await session.refresh(plan)

    return MealPlanRead.model_validate(plan)


@router.get("/{plan_id}/profile-status")
async def check_profile_status(
    plan_id: uuid.UUID,
    user: Annotated[User, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict:
    """Check if profile has changed since this plan was created.

    Returns information about whether the plan may need regeneration
    due to profile changes.
    """
    plan = await PlanService.get_by_id(session, plan_id, user.id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found",
        )

    profile = await ProfileService.get_by_user_id(session, user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Baby profile not found",
        )

    return await PlanService.check_profile_changed_since_plan(
        session, profile, plan
    )

