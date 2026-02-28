"""Security utilities for JWT tokens and password hashing."""

import logging
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
import bcrypt
from pydantic import ValidationError

from backend.app.core.config import settings
from backend.app.models.user import TokenData, UserRole

logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )
    except ValueError:
        return False


def create_access_token(
    user_id: str,
    email: str,
    role: UserRole,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a JWT access token.
    
    Args:
        user_id: User's UUID
        email: User's email
        role: User's role (student, staff, admin)
        expires_delta: Optional custom expiration time
    
    Returns:
        JWT token string
    """
    to_encode = {
        "sub": user_id,
        "email": email,
        "role": role.value,
        "iat": datetime.utcnow(),
    }
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Default expiration based on settings
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire})
    
    try:
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )
        logger.debug(f"JWT token created for user {email} (expires: {expire})")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Failed to create JWT token: {str(e)}")
        raise


def decode_token(token: str) -> Optional[TokenData]:
    """
    Decode and validate a JWT token.
    
    Args:
        token: JWT token string
    
    Returns:
        TokenData if valid, None if invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        role_str: str = payload.get("role")
        
        if user_id is None or email is None or role_str is None:
            logger.warning("Token missing required fields")
            return None
        
        role = UserRole(role_str)
        token_data = TokenData(user_id=user_id, email=email, role=role)
        logger.debug(f"Token successfully decoded for user {email}")
        return token_data
        
    except JWTError as e:
        logger.warning(f"Invalid JWT token: {str(e)}")
        return None
    except ValidationError as e:
        logger.warning(f"Token validation error: {str(e)}")
        return None
