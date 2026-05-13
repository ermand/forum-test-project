from uuid import UUID
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentUserDep
from src.models.user import User
from src.schemas.user import UserCreate, UserProfileResponse
from core.auth.password import DUMMY_PASSWORD_HASH, hash_password, verify_password
from src.utils import PaginationParams, paginate
from src.models.posts import Post
from src.services.post_service import post_loader_options


async def create_user(db: AsyncSession, user: UserCreate):
    username = user.username.lower()
    email = user.email.lower()
    result = await db.execute(
        select(User).where(User.username == username)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already exists")

    result = await db.execute(
        select(User).where(User.email == email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already exists")
    db_user = User(
        username=username,
        email=email,
        password_hash=hash_password(user.password),
    )
    db.add(db_user)
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise
    await db.refresh(db_user)
    return db_user


async def get_user_by_id(db: AsyncSession, user_id: UUID,params: PaginationParams):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    post_statement = (
        select(Post)
        .options(*post_loader_options())
        .where(Post.user_id == user_id)
        .order_by(Post.created_at.desc())
        .execution_options(populate_existing=True)
    )
    paginated_posts = await paginate(db, post_statement, params)

    return {
        "user_info": user,
        "posts": paginated_posts
    }


async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).filter(User.email == email.lower()))
    return result.scalar_one_or_none()

async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(User).where(User.username == username.lower()))
    return result.scalar_one_or_none()


async def get_user_profile(db: AsyncSession, user:CurrentUserDep, params: PaginationParams):
    post_statement = (
        select(Post)
        .options(*post_loader_options())
        .where(Post.user_id == user.id)
        .order_by(Post.created_at.desc())
        .execution_options(populate_existing=True)
    )
    paginated_posts = await paginate(db, post_statement, params)

    return {
        "user_info": user,
        "posts": paginated_posts
    }


async def authenticate_user(db: AsyncSession, username: str, password: str):
    user = await get_user_by_username(db, username.lower())

    if not user:
        return False

    if not verify_password(password, user.password_hash):
        return False

    return user
