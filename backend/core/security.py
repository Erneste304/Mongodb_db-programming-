# pyrefly: ignore [missing-import]
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from backend.core.config import settings
from backend.models.user import User
from typing import Optional

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Get current user from JWT token"""

    def credentials_exception(reason: str = "Could not validate credentials"):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=reason,
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.SECRET_KEY,
                             algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        print(f"DEBUG: JWT sub claim (user_id): {user_id}")
        if user_id is None:
            raise credentials_exception("Token missing 'sub' claim")
    except JWTError as e:
        print(f"DEBUG: JWT Error: {e}")
        raise credentials_exception(f"JWT Decode Error: {str(e)}")

    from beanie import PydanticObjectId
    import asyncio

    # Retry up to 5 times (5 seconds total) to handle startup race condition
    # where Beanie ODM hasn't finished initializing when the first request arrives.
    last_error = None
    for attempt in range(5):
        try:
            user = await User.get(PydanticObjectId(user_id), fetch_links=True)
            if user:
                print(f"DEBUG: User lookup result: {user}")
                if not user.is_active:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN, detail="User account is disabled")
                return user
            raise credentials_exception("User not found in database")
        except Exception as e:
            last_error = e
            if "CollectionWasNotInitialized" in type(e).__name__ or "CollectionWasNotInitialized" in str(e):
                print(
                    f"DEBUG: Beanie not ready yet, retrying in 1s (attempt {attempt + 1}/5)...")
                await asyncio.sleep(1)
            else:
                raise credentials_exception(f"Authentication Error: {str(e)}")
    else:
        # All retries exhausted
        print(
            f"DEBUG: Beanie still not initialized after 5 retries: {last_error}")
        raise credentials_exception(
            "Database not ready. Please refresh in a moment.")


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def require_role(role_name: str):
    """Dependency to require specific role"""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role.name != role_name and current_user.role.name != "superadmin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role_name}' required"
            )
        return current_user
    return role_checker


def require_role_level(min_level: int):
    """Dependency to require minimum role level"""
    async def level_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role.level > min_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role level {min_level} or higher required"
            )
        return current_user
    return level_checker
