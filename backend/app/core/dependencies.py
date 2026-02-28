"""FastAPI dependencies for authentication and authorization."""

import logging
from typing import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.core.security import decode_token
from backend.app.models.user import User, UserRole, TokenData

logger = logging.getLogger(__name__)

# OAuth2 scheme for Bearer token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.
    
    Raises:
        HTTPException 401: If token is invalid or user not found
    
    Returns:
        User object
    """
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = decode_token(token)
    if token_data is None:
        raise credential_exception
    
    # Get user from database
    from sqlalchemy import select
    
    result = await db.execute(
        select(User).where(User.id == token_data.user_id)
    )
    user = result.scalars().first()
    
    if user is None:
        logger.warning(f"User {token_data.user_id} not found in database")
        raise credential_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    
    return user


def require_role(*allowed_roles: UserRole) -> Callable:
    """
    Factory function to create a dependency that checks if user has required role.
    
    Usage:
        async def protected_endpoint(
            current_user: User = Depends(require_role(UserRole.ADMIN))
        ):
            ...
    
    Args:
        allowed_roles: One or more UserRole values
    
    Returns:
        Dependency function
    """
    async def check_role(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role not in allowed_roles:
            logger.warning(
                f"User {current_user.email} (role={current_user.role}) "
                f"attempted to access endpoint requiring {allowed_roles}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[r.value for r in allowed_roles]}",
            )
        return current_user
    
    return check_role


# Convenience dependencies for common role checks
def require_student(current_user: User = Depends(require_role(UserRole.STUDENT))) -> User:
    """Require STUDENT role."""
    return current_user


def require_staff(current_user: User = Depends(require_role(UserRole.STAFF))) -> User:
    """Require STAFF role."""
    return current_user


def require_admin(current_user: User = Depends(require_role(UserRole.ADMIN))) -> User:
    """Require ADMIN role."""
    return current_user


def require_staff_or_admin(
    current_user: User = Depends(require_role(UserRole.STAFF, UserRole.ADMIN))
) -> User:
    """Require STAFF or ADMIN role."""
    return current_user
