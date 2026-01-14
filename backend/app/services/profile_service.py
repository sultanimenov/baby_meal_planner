"""Service for baby profile operations."""

import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.baby_profile import BabyProfile
from app.schemas.profile import BabyProfileCreate, BabyProfileUpdate


class ProfileService:
    """Service for managing baby profiles."""

    @staticmethod
    async def get_by_user_id(session: AsyncSession, user_id: uuid.UUID) -> BabyProfile | None:
        """Get baby profile by user ID."""
        result = await session.execute(
            select(BabyProfile).where(BabyProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(
        session: AsyncSession, user_id: uuid.UUID, profile_data: BabyProfileCreate
    ) -> BabyProfile:
        """Create a new baby profile."""
        profile = BabyProfile(user_id=user_id, **profile_data.model_dump())
        session.add(profile)
        await session.commit()
        await session.refresh(profile)
        return profile

    @staticmethod
    async def update(
        session: AsyncSession,
        profile: BabyProfile,
        profile_data: BabyProfileUpdate,
    ) -> BabyProfile:
        """Update an existing baby profile."""
        update_dict = profile_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(profile, field, value)
        await session.commit()
        await session.refresh(profile)
        return profile

    @staticmethod
    async def delete(session: AsyncSession, profile: BabyProfile) -> None:
        """Delete a baby profile."""
        await session.delete(profile)
        await session.commit()


