from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Path, status, Query, Form , Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from core.auth.dependencies import CurrentUserDep
from core.db_connection.session import SessionDep
from src.schemas.comment import CommentCreate, CommentResponse, CommentUpdate
from src.services import comment_service
from src.utils.schemas import ApiResponse, PaginationParams
from src.utils.schemas import PaginatedResponse

router = APIRouter(tags=["Comments"])
limiter = Limiter(key_func=get_remote_address)

@router.post(
    "/posts/{id}/comments", response_model=ApiResponse[CommentResponse], status_code=status.HTTP_201_CREATED, )
async def create_comment(
        _request:Request,
        id: Annotated[UUID, Path()],
        comment: Annotated[CommentCreate, Form()],
        db: SessionDep,
    current_user: CurrentUserDep,
):
    comment.post_id = id
    return await comment_service.comment_create(
        db, comment_data=comment, user_id=current_user.id
    )


@router.get("/posts/{id}/comments", response_model=ApiResponse[PaginatedResponse[CommentResponse]])
async def read_comments(
        _request: Request,
        id: Annotated[UUID, Path()],
        db: SessionDep,
        params: Annotated[PaginationParams, Query()],
):
    comments = await comment_service.get_post_comments(db, post_id=id, params=params)

    return ApiResponse(data=comments)


@router.put("/comments/{id}", response_model=ApiResponse[CommentResponse])
async def update_comment(
        id: Annotated[UUID, Path()],
        comment: Annotated[CommentUpdate, Form()],
        db: SessionDep,
        current_user: CurrentUserDep,
):
    return await comment_service.update_post_comment(
        db, comment_data=comment, comment_id=id, user_id=current_user.id
    )


@router.delete("/comments/{id}", status_code=status.HTTP_200_OK)
async def delete_comment(
        id: Annotated[UUID, Path()],
        db: SessionDep,
        current_user: CurrentUserDep,
):
    return await comment_service.delete_post_comment(
        db, comment_id=id, user_id=current_user.id
    )
