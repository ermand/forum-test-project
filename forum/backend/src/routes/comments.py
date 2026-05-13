from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Path, status, Query, Form, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from core.auth.dependencies import CurrentUserDep
from core.db_connection.session import SessionDep

from src.schemas.comment import CommentCreate, CommentResponse, CommentUpdate
from src.services import comment_service
from src.utils.schemas import ApiResponse, PaginationParams, PaginatedResponse

router = APIRouter(tags=["Comments"])
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/posts/{post_id}/comments",
    response_model=ApiResponse[CommentResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
        _request: Request,
        comment: Annotated[CommentCreate, Form()],
        db: SessionDep,
        current_user: CurrentUserDep,
):
    db_comment = await comment_service.comment_create(
        db,
        comment_data=comment,
        user_id=current_user.id,
    )

    return ApiResponse(
        message="Comment created",
        data=CommentResponse.model_validate(db_comment),
    )


@router.get(
    "/posts/{post_id}/comments",
    response_model=ApiResponse[PaginatedResponse[CommentResponse]],
)
async def read_comments(
        _request: Request,
        post_id: Annotated[UUID, Path()],
        db: SessionDep,
        params: Annotated[PaginationParams, Query()],
):
    result = await comment_service.get_post_comments(
        db,
        post_id=post_id,
        params=params,
    )

    return ApiResponse(
        message="Comments fetched",
        data=result,
    )


@router.put(
    "/comments/{comment_id}",
    response_model=ApiResponse[CommentResponse],
)
async def update_comment(
        comment_id: Annotated[UUID, Path()],
        comment: Annotated[CommentUpdate, Form()],
        db: SessionDep,
        current_user: CurrentUserDep,
):
    db_comment = await comment_service.update_post_comment(
        db,
        comment_id=comment_id,
        comment_data=comment,
        user_id=current_user.id,
    )

    return ApiResponse(
        message="Comment updated",
        data=CommentResponse.model_validate(db_comment),
    )


@router.delete(
    "/comments/{comment_id}",
    response_model=ApiResponse[bool],
)
async def delete_comment(
        comment_id: Annotated[UUID, Path()],
        db: SessionDep,
        current_user: CurrentUserDep,
):
    result = await comment_service.delete_post_comment(
        db,
        comment_id=comment_id,
        user_id=current_user.id,
    )

    return ApiResponse(
        message="Comment deleted",
        data=result,
    )
