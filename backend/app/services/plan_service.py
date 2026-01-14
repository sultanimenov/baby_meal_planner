"""Service for meal plan operations."""

import uuid
from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.baby_profile import BabyProfile
from app.models.meal_plan import MealPlan
from app.planner.graph import create_planner_graph
from app.planner.state import PlannerState

# Profile fields that affect meal plan generation
PLAN_AFFECTING_FIELDS = {
    "feeding_style",
    "meals_per_day",
    "dietary_preference",
    "allergens",
    "avoid_list",
    "max_prep_minutes",
}


class PlanService:
    """Service for managing meal plans."""

    @staticmethod
    async def generate_plan(
        session: AsyncSession,
        user_id: uuid.UUID,
        baby_profile_id: uuid.UUID,
        num_days: int,
        plan_style: str,
        introduce_new_foods: bool = False,
    ) -> MealPlan:
        """Generate a new meal plan using LangGraph.

        Args:
            session: Database session
            user_id: User ID
            baby_profile_id: Baby profile ID
            num_days: Number of days (3 or 7)
            plan_style: Plan style (variety or simple_repeats)
            introduce_new_foods: Whether to introduce new foods

        Returns:
            Generated MealPlan
        """
        # Create initial state as dict
        initial_state = {
            "user_id": str(user_id),
            "baby_profile_id": str(baby_profile_id),
            "num_days": num_days,
            "plan_style": plan_style,
            "introduce_new_foods": introduce_new_foods,
        }

        # Create and run graph with session bound
        graph = create_planner_graph(session)

        # Run graph with initial state
        final_state_dict = await graph.ainvoke(initial_state)

        # Load persisted plan
        plan_id = final_state_dict.get("meal_plan_id")
        if not plan_id:
            raise ValueError("Plan generation failed - no plan ID returned")

        plan = await session.get(MealPlan, uuid.UUID(plan_id))
        if not plan:
            raise ValueError(f"Plan {plan_id} not found after generation")

        return plan

    @staticmethod
    async def get_by_id(
        session: AsyncSession, plan_id: uuid.UUID, user_id: uuid.UUID
    ) -> MealPlan | None:
        """Get meal plan by ID (user must own it).

        Args:
            session: Database session
            plan_id: Plan ID
            user_id: User ID (for authorization)

        Returns:
            MealPlan or None
        """
        result = await session.execute(
            select(MealPlan).where(
                MealPlan.id == plan_id, MealPlan.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_by_user(
        session: AsyncSession, user_id: uuid.UUID, limit: int = 10
    ) -> list[MealPlan]:
        """List meal plans for a user.

        Args:
            session: Database session
            user_id: User ID
            limit: Maximum number of plans to return

        Returns:
            List of MealPlans
        """
        result = await session.execute(
            select(MealPlan)
            .where(MealPlan.user_id == user_id)
            .order_by(MealPlan.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def check_profile_changed_since_plan(
        session: AsyncSession,
        profile: BabyProfile,
        plan: MealPlan,
    ) -> dict[str, Any]:
        """Check if profile has changed since plan was created.

        Compares plan-affecting fields to determine if the plan
        may need regeneration.

        Args:
            session: Database session
            profile: Current baby profile
            plan: Meal plan to check against

        Returns:
            Dict with 'changed' bool and 'changed_fields' list
        """
        # Get plan's generation metadata
        metadata = plan.generation_metadata or {}
        profile_snapshot = metadata.get("profile_snapshot", {})

        if not profile_snapshot:
            # No snapshot stored - can't determine if changed
            return {"changed": False, "changed_fields": []}

        changed_fields = []

        for field in PLAN_AFFECTING_FIELDS:
            current_value = getattr(profile, field, None)
            snapshot_value = profile_snapshot.get(field)

            # Handle list comparisons
            if isinstance(current_value, list) and isinstance(snapshot_value, list):
                if set(current_value) != set(snapshot_value):
                    changed_fields.append(field)
            elif current_value != snapshot_value:
                changed_fields.append(field)

        return {
            "changed": len(changed_fields) > 0,
            "changed_fields": changed_fields,
        }

    @staticmethod
    def create_profile_snapshot(profile: BabyProfile) -> dict[str, Any]:
        """Create a snapshot of plan-affecting profile fields.

        Args:
            profile: Baby profile

        Returns:
            Dict with field values
        """
        return {
            field: getattr(profile, field, None)
            for field in PLAN_AFFECTING_FIELDS
        }

