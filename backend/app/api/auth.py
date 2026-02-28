"""Authentication API endpoints."""

import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)
from backend.app.core.dependencies import get_current_user
from backend.app.models.user import (
    User,
    UserRole,
    UserCreate,
    UserRead,
    UserLogin,
    Token,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])

# In-memory token blacklist for logout (in production, use Redis)
# Format: {token_jti: expiration_datetime}
_token_blacklist = {}


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserRead:
    """
    Register a new user.
    
    In v1, registration is open. In v2+, consider making this admin-only.
    
    Args:
        user_data: User registration data (email, password, name, student_id)
        db: Database session
    
    Returns:
        Newly created user (without password)
    
    Raises:
        409: Email already registered
    """
    # Check if email already exists
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    existing_user = result.scalars().first()
    
    if existing_user is not None:
        logger.warning(f"Registration attempt with existing email: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    
    # Create new user
    new_user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        student_id=user_data.student_id,
        role=UserRole.STUDENT,  # Default role is student
        is_active=True,
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    logger.info(f"New user registered: {user_data.email}")
    return UserRead.model_validate(new_user)


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> Token:
    """
    Login with email and password.
    
    Returns JWT access token if credentials are valid.
    
    Args:
        credentials: Email and password
        db: Database session
    
    Returns:
        JWT token and user info
    
    Raises:
        401: Invalid credentials
    """
    # Find user by email
    result = await db.execute(
        select(User).where(User.email == credentials.email)
    )
    user = result.scalars().first()
    
    if user is None or not verify_password(credentials.password, user.hashed_password):
        logger.warning(f"Failed login attempt for: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    
    # Create JWT token
    access_token = create_access_token(
        user_id=str(user.id),
        email=user.email,
        role=user.role,
    )
    
    logger.info(f"User logged in: {user.email}")
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserRead.model_validate(user),
    )


@router.get("/me", response_model=UserRead)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> UserRead:
    """
    Get current authenticated user's information.
    
    Args:
        current_user: Current authenticated user (from JWT)
    
    Returns:
        User information
    """
    return UserRead.model_validate(current_user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    token: str = Depends(get_current_user),
) -> None:
    """
    Logout user by blacklisting token.
    
    Note: In this simple implementation, we use an in-memory blacklist.
    For production, use Redis or a database table.
    
    Args:
        token: Current user (implicitly validates token)
    
    Returns:
        No content (204)
    """
    # In a real implementation, you would:
    # - Store token in blacklist (Redis)
    # - Clear frontend JWT token
    # This is a simplified version for local development
    logger.info(f"User logged out")


@router.post("/refresh", response_model=Token)
async def refresh_token(
    current_user: User = Depends(get_current_user),
) -> Token:
    """
    Refresh JWT token (extend expiration).
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        New JWT token
    """
    new_token = create_access_token(
        user_id=str(current_user.id),
        email=current_user.email,
        role=current_user.role,
    )
    
    logger.info(f"Token refreshed for user: {current_user.email}")
    
    return Token(
        access_token=new_token,
        token_type="bearer",
        user=UserRead.model_validate(current_user),
    )
