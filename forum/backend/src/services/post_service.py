from uuid import UUID
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from src.utils.pagination import paginate
from src.models.posts import Post
from src.schemas.posts import PostCreate, PostUpdate
from src.utils import PaginationParams


async def create_new_post(db: AsyncSession, post_data: PostCreate, user_id: UUID):
    db_post = Post(
        title=post_data.title,
        content=post_data.content,
        user_id=user_id
    )
    db.add(db_post)
    await db.commit()
    await db.refresh(db_post)
    return db_post


async def get_posts(db: AsyncSession, params: PaginationParams):
    statement = select(Post).order_by(Post.created_at.desc())
    return await paginate(db, statement, params)


async def get_post(db: AsyncSession, post_id: UUID):
    result = await db.execute(
        select(Post).filter(Post.id == post_id)
    )
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    return post


async def update_post(db: AsyncSession, post_id: UUID, post_update: PostUpdate, user_id: UUID):
    result = await db.execute(
        select(Post).filter(Post.id == post_id)
    )
    db_post = result.scalar_one_or_none()

    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    if db_post.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to edit this post"
        )

    if post_update.title:
        db_post.title = post_update.title
    if post_update.content:
        db_post.content = post_update.content

    await db.commit()
    await db.refresh(db_post)
    return db_post


async def delete_post(db: AsyncSession, post_id: UUID, user_id: UUID):
    result = await db.execute(select(Post).filter(Post.id == post_id))
    db_post = result.scalar_one_or_none()

    if db_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    if db_post.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this post",
        )

    await db.delete(db_post)
    await db.commit()

    return True
