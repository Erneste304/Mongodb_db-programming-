from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from beanie.operators import Or
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from backend.core.config import settings
from backend.models.user import User, Role
from backend.core.exceptions import InvalidCredentials

router = APIRouter(prefix="/auth", tags=["authentication"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(
            timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Authenticate user and return JWT token"""
    try:
        # Use dictionary query to avoid AttributeError with User.username in Beanie/Pydantic v2
        user = await User.find_one(
            {
                "$or": [
                    {"username": request.username.lower() if request.username else ""},
                    {"email": request.username.lower() if request.username else ""}
                ]
            },  # This comma is important if fetch_links is a separate argument
            fetch_links=True
        )  # Added missing closing parenthesis for User.find_one

        if not user or not verify_password(request.password, getattr(user, "password_hash", "")):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        if not getattr(user, "is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled"
            )

        # Update last login
        try:
            user.last_login = datetime.now(timezone.utc)
            await user.save()
        except Exception:
            # Non-critical: allow login even if last_login update fails
            pass

        # Safely get role name (handles Link, None, or string types)
        role_name = "unknown"
        if hasattr(user, 'role') and user.role:
            if hasattr(user.role, 'name'):
                role_name = user.role.name
            else:
                role_name = str(user.role)

        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.id), "username": getattr(user, "username", "unknown"),
                  "role": str(role_name)}
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user={
                "id": str(user.id),
                "username": getattr(user, "username", "unknown"),
                "email": getattr(user, "email", ""),
                "role": role_name,
                "full_name": getattr(user, "full_name", ""),
                "employee_id": getattr(user, "employee_id", "")
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        # Log the actual error to terminal for debugging
        print(
            f"\n❌ [BACKEND ERROR] Login failed for {request.username}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {str(e)}"
        )
