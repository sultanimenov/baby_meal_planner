"""Baby profile API endpoints."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import current_user
from app.core.database import get_session
from app.models.baby_profile import BabyProfile
from app.models.user import User
from app.schemas.profile import BabyProfileCreate, BabyProfileRead, BabyProfileUpdate
from app.services.profile_service import ProfileService

router = APIRouter()


async def get_current_profile(
    user: Annotated[User, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> BabyProfile:
    """Get current user's baby profile or raise 404."""
    profile = await ProfileService.get_by_user_id(session, user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Baby profile not found",
        )
    return profile


@router.get("/me", response_model=BabyProfileRead)
async def get_profile(
    profile: Annotated[BabyProfile, Depends(get_current_profile)],
) -> BabyProfileRead:
    """Get current user's baby profile."""
    return BabyProfileRead(
        **profile.model_dump(),
        age_in_months=profile.age_in_months,
    )


@router.post("", response_model=BabyProfileRead, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile_data: BabyProfileCreate,
    user: Annotated[User, Depends(current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> BabyProfileRead:
    """Create a new baby profile for the current user."""
    # Check if profile already exists
    existing = await ProfileService.get_by_user_id(session, user.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Baby profile already exists for this user",
        )

    profile = await ProfileService.create(session, user.id, profile_data)
    return BabyProfileRead(
        **profile.model_dump(),
        age_in_months=profile.age_in_months,
    )


@router.put("/me", response_model=BabyProfileRead)
async def update_profile(
    profile_data: BabyProfileUpdate,
    profile: Annotated[BabyProfile, Depends(get_current_profile)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> BabyProfileRead:
    """Update current user's baby profile."""
    updated_profile = await ProfileService.update(session, profile, profile_data)
    return BabyProfileRead(
        **updated_profile.model_dump(),
        age_in_months=updated_profile.age_in_months,
    )


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    profile: Annotated[BabyProfile, Depends(get_current_profile)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    """Delete current user's baby profile."""
    await ProfileService.delete(session, profile)


