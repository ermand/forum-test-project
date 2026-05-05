from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy import select
from src.models import Post, Comment

from src.schemas.comment import CommentCreate, CommentUpdate, CommentResponse
from src.utils import ApiResponse, PaginationParams, paginate


async def comment_create( db: AsyncSession,comment_data: CommentCreate,user_id: UUID,) -> ApiResponse[CommentResponse]:
    if comment_data.post_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="post_id is required",
        )
    post = await db.get(Post, comment_data.post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    new_comment = Comment(
        content=comment_data.content, user_id=user_id, post_id=comment_data.post_id
    )
    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)

    comment_response = CommentResponse.model_validate(new_comment)
    return ApiResponse[CommentResponse](
        message="Comment created",
        data=comment_response,
    )


async def get_post_comments(db: AsyncSession, post_id: UUID, params: PaginationParams):
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    statement = (
        select(Comment)
        .where(Comment.post_id == post_id)
        .order_by(Comment.created_at.asc())
    )
    return await paginate(db, statement, params)


async def update_post_comment(
        db: AsyncSession, comment_id: UUID, comment_data: CommentUpdate, user_id: UUID
) -> ApiResponse[CommentResponse]:
    comment = await db.get(Comment, comment_id)

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    if comment.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )

    comment.content = comment_data.content

    await db.commit()
    await db.refresh(comment)
    return ApiResponse[CommentResponse](
        message="Comment updated",
        data=CommentResponse.model_validate(comment),
    )


async def delete_post_comment(
        db: AsyncSession, comment_id: UUID, user_id: UUID) -> ApiResponse[None]:
    comment = await db.get(Comment, comment_id)

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )
    if comment.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )

    await db.delete(comment)
    await db.commit()
    return ApiResponse[None](message="Comment deleted")
