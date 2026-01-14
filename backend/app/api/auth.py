"""Authentication endpoints using fastapi-users."""

import uuid

from fastapi import APIRouter, Depends
from fastapi_users import FastAPIUsers, schemas
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.manager import BaseUserManager
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_session
from app.core.security import SECRET
from app.models.user import User


# User schemas for fastapi-users
class UserRead(schemas.BaseUser[uuid.UUID]):
    """Schema for reading a user."""

    pass


class UserCreate(schemas.BaseUserCreate):
    """Schema for creating a user."""

    pass


class UserUpdate(schemas.BaseUserUpdate):
    """Schema for updating a user."""

    pass


class UserManager(BaseUserManager[User, uuid.UUID]):
    """User manager for fastapi-users."""

    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    def parse_id(self, value: str) -> uuid.UUID:
        """Parse user ID from string to UUID."""
        return uuid.UUID(value)

    async def on_after_register(self, user: User, request=None):
        """Called after user registration."""
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(self, user: User, token: str, request=None):
        """Called after forgot password request."""
        print(f"User {user.id} has requested password reset. Token: {token}")

    async def on_after_update(self, user: User, update_dict: dict, request=None):
        """Called after user update."""
        print(f"User {user.id} has been updated.")

    async def on_after_verify(self, user: User, request=None):
        """Called after email verification."""
        print(f"User {user.id} has been verified.")


async def get_user_manager(session: AsyncSession = Depends(get_session)):
    """Get user manager instance."""
    from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

    user_db = SQLAlchemyUserDatabase(session, User)
    yield UserManager(user_db)


# JWT Strategy
def get_jwt_strategy() -> JWTStrategy:
    """Get JWT authentication strategy."""
    return JWTStrategy(
        secret=SECRET,
        lifetime_seconds=settings.access_token_expire_minutes * 60,
    )


# Authentication backend
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

# FastAPI Users instance
fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

# Current user dependencies
current_user = fastapi_users.current_user(active=True)
current_verified_user = fastapi_users.current_user(active=True, verified=True)

# Router
router = APIRouter()

# Include fastapi-users routers
router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

router.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)

router.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)

router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

