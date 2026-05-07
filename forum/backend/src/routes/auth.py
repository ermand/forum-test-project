from typing import Annotated
from fastapi import APIRouter, Depends, Form, HTTPException, status , Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from core.auth.jwt import create_access_token
from core.db_connection.session import SessionDep
from src.config.settings import  SettingsDep, Settings
from src.schemas.token import Token
from src.schemas.user import UserCreate, UserResponse
from src.services import user_service
import secrets
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.refresh_token import RefreshToken
from src.config.settings import settings
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/auth", tags=["Authentication"])


def registration_form(
        username: Annotated[str, Form(min_length=3, max_length=50)],
        email: Annotated[EmailStr, Form()],
        password: Annotated[str, Form(min_length=8, max_length=128)],
) -> UserCreate:
    return UserCreate(username=username, email=email, password=password)


async def issue_token_pair(db: AsyncSession, user, settings: Settings) -> Token:
    access_token = create_access_token(subject=user.username)
    refresh_token = await create_refresh_tokens(db, user)
    await db.commit()
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
@limiter.limit("10/minute")
async def register_user(
        request : Request,
        user_data: Annotated[UserCreate, Depends(registration_form)],
        db: SessionDep,
):
    existing_user = await user_service.get_user_by_email(db, email=user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    existing_username = await user_service.get_user_by_username(
        db, username=user_data.username
    )
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already registered")

    new_user = await user_service.create_user(db=db, user=user_data)

    return new_user


@router.post("/token", response_model=Token)
@router.post("/login", response_model=Token, include_in_schema=False)
@limiter.limit("10/minute")
async def login_for_tokens(
        request: Request,
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: SessionDep,
        settings: SettingsDep,
):
    user = await user_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return await issue_token_pair(db, user, settings)


async def create_refresh_tokens(db: AsyncSession, user):
    token_str = secrets.token_urlsafe(32)
    expiration_date = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    db_token = RefreshToken(
        token_hash=token_str,
        user_id=user.id,
        expires_at=expiration_date
    )
    db.add(db_token)
    await db.flush()

    return token_str
