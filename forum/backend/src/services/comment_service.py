from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import Comment, Post
from src.schemas.comment import CommentCreate, CommentUpdate
from src.utils import PaginationParams, paginate


async def comment_create(
    db: AsyncSession,
    comment_data: CommentCreate,
    user_id: UUID,
) -> Comment:
    post = await db.get(Post, comment_data.post_id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    new_comment = Comment(
        content=comment_data.content,
        user_id=user_id,
        post_id=comment_data.post_id,
    )

    db.add(new_comment)

    await db.commit()
    await db.refresh(new_comment)

    return new_comment


async def get_post_comments(
    db: AsyncSession,
    post_id: UUID,
    params: PaginationParams,
):
    post = await db.get(Post, post_id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    statement = (
        select(Comment)
        .options(
            selectinload(Comment.author),
            selectinload(Comment.post),
        )
        .where(Comment.post_id == post_id)
        .order_by(Comment.created_at.asc())
    )

    return await paginate(db, statement, params)


async def update_post_comment(
    db: AsyncSession,
    comment_id: UUID,
    comment_data: CommentUpdate,
    user_id: UUID,
) -> Comment:
    stmt = select(Comment).where(
        Comment.id == comment_id,
        Comment.user_id == user_id,
    )

    result = await db.execute(stmt)
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or not authorized",
        )

    comment.content = comment_data.content

    await db.commit()
    await db.refresh(comment)

    return comment


async def delete_post_comment(
    db: AsyncSession,
    comment_id: UUID,
    user_id: UUID,
) -> bool:
    stmt = select(Comment).where(
        Comment.id == comment_id,
        Comment.user_id == user_id,
    )

    result = await db.execute(stmt)
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or not authorized",
        )

    await db.delete(comment)
    await db.commit()

    return True
