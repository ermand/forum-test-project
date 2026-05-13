from uuid import UUID
from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, with_expression
from starlette import status
from src.models.comments import Comment
from src.utils.pagination import paginate
from src.models.posts import Post
from src.schemas.posts import PostCreate, PostUpdate
from src.utils import PaginationParams


def post_comments_count_expression():
    return (
        select(func.count(Comment.id))
        .where(Comment.post_id == Post.id)
        .correlate(Post)
        .scalar_subquery()
    )


def post_loader_options(*, include_comments: bool = False):
    options = [
        selectinload(Post.owner),
        with_expression(Post.comments_count, post_comments_count_expression()),
    ]
    if include_comments:
        options.append(selectinload(Post.comments))
    return options


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
    statement = (
        select(Post)
        .options(*post_loader_options())
        .order_by(Post.created_at.desc())
        .execution_options(populate_existing=True)
    )
    return await paginate(db, statement, params)


async def get_post(db: AsyncSession, post_id: UUID):
    result = await db.execute(
        select(Post)
        .options(*post_loader_options(include_comments=True))
        .where(Post.id == post_id)
        .execution_options(populate_existing=True)
    )
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    return post


async def update_post(db: AsyncSession, post_id: UUID, post_update: PostUpdate, user_id: UUID):
    stmt = select(Post).where(
        Post.id == post_id,
        Post.user_id == user_id
    )

    result = await db.execute(stmt)
    db_post = result.scalar_one_or_none()

    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found or not authorized")

    update_data = post_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_post, key, value)

    await db.commit()
    await db.refresh(db_post)
    return db_post


async def delete_post(db: AsyncSession, post_id: UUID, user_id: UUID):
    db_post = await db.get(Post, post_id)

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
