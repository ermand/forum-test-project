import hashlib
import secrets
from datetime import datetime, timezone , timedelta
from fastapi import HTTPException, status
from pydantic import EmailStr
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.jwt import create_access_token
from src.models.refresh_token import RefreshToken
from src.schemas.user import UserCreate
from src.schemas.token import Token
from src.config.settings import Settings


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def registration_form(
        username: str,
        email: EmailStr,
        password: str,
) -> UserCreate:
    return UserCreate(
        username=username,
        email=email,
        password=password
    )


async def register_user_service(db, user_data, user_service):
    username = user_data.username.lower()
    email = user_data.email.lower()

    existing_user = await user_service.get_user_by_username(db, username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    existing_email = await user_service.get_user_by_email(db, email)
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    return await user_service.create_user(
        db=db,
        user=UserCreate(
            username=username,
            email=email,
            password=user_data.password
        )
    )


async def login_user_service(db, username, password, user_service, issue_token_pair, settings):
    user = await user_service.authenticate_user(
        db,
        username.lower(),
        password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return await issue_token_pair(db, user, settings)

async def create_refresh_token(db: AsyncSession, user, settings: Settings):
    token = secrets.token_urlsafe(32)

    db_token = RefreshToken(
        token_hash=hash_refresh_token(token),
        user_id=user.id,
        expires_at=datetime.now(timezone.utc)
        + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )

    db.add(db_token)
    await db.commit()

    return token


async def issue_token_pair(db: AsyncSession, user, settings: Settings) -> Token:
    access_token = create_access_token(subject=user.username)
    refresh_token = await create_refresh_token(db, user, settings)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

from sqlalchemy.orm import selectinload

async def refresh_token_service(db: AsyncSession, refresh_token: str, settings: Settings):

    hashed = hash_refresh_token(refresh_token)

    result = await db.execute(
        select(RefreshToken)
        .options(selectinload(RefreshToken.user))
        .where(RefreshToken.token_hash == hashed)
    )
    token_db = result.scalar_one_or_none()

    if not token_db:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    expires_at = token_db.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < datetime.now(timezone.utc):
        await db.delete(token_db)
        await db.commit()
        raise HTTPException(status_code=401, detail="Refresh token expired")

    user_id = token_db.user_id
    user_username = token_db.user.username


    await db.delete(token_db)

    new_refresh = secrets.token_urlsafe(32)
    db.add(
        RefreshToken(
            token_hash=hash_refresh_token(new_refresh),
            user_id=user_id,
            expires_at=datetime.now(timezone.utc)
                       + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
    )


    access_token = create_access_token(subject=user_username)

    await db.commit()

    return {
        "access_token": access_token,
        "refresh_token": new_refresh,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }

async def logout_user_service(db: AsyncSession, user):
    await db.execute(
        delete(RefreshToken).where(RefreshToken.user_id == user.id)
    )
    await db.commit()
    return {"message": "Logged out successfully"}