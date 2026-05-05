from uuid import UUID
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.posts import Post
from src.models.user import User
from src.schemas.user import UserCreate
from core.auth.password import DUMMY_PASSWORD_HASH, hash_password, verify_password
from src.utils import PaginationParams, paginate


async def create_user(db: AsyncSession, user: UserCreate):
    password = hash_password(user.password)

    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=password,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_user_by_id(db: AsyncSession, user_id: UUID):
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalar_one_or_none()


async def get_user_profile(db: AsyncSession, user_id: UUID, params: PaginationParams):
    user = await get_user_by_id(db, user_id)

    post_statement = (
        select(Post)
        .where(Post.user_id == user_id)
        .order_by(Post.created_at.desc())
    )

    paginated_posts = await paginate(db, post_statement, params)

    return {
        "user_info": user,
        "posts": paginated_posts
    }


async def authenticate_user(db: AsyncSession, email: str, password: str):
    user = await get_user_by_email(db, email)

    if not user:
        verify_password(password, DUMMY_PASSWORD_HASH)
        return False

    if not verify_password(password, user.password_hash):
        return False

    return user
