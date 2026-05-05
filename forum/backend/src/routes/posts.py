from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Path, status, Query, Form , Request
from slowapi import Limiter
from slowapi.util import get_remote_address
limiter = Limiter(key_func=get_remote_address)
from core.auth.dependencies import CurrentUserDep
from core.db_connection.session import SessionDep
from src.schemas.posts import PostCreate, PostResponse, PostUpdate
from src.services import post_service
from src.utils import ApiResponse, PaginatedResponse, PaginationParams

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/", response_model=ApiResponse[PaginatedResponse[PostResponse]])
async def read_posts(_request:Request,db: SessionDep, params: Annotated[PaginationParams, Query()]):
    data = await post_service.get_posts(db, params=params)
    return ApiResponse(data=data)


@router.get("/{id}", response_model=ApiResponse[PostResponse])
async def read_single_post(_request:Request,id: Annotated[UUID, Path()], db: SessionDep):
    post = await post_service.get_post(db, id)
    return ApiResponse(data=post)


@router.post("/", response_model=ApiResponse[PostResponse], status_code=status.HTTP_201_CREATED)
async def create_post(
        _request: Request,
        post: Annotated[PostCreate, Form()],
        db: SessionDep,
        current_user: CurrentUserDep,
):
    post = await post_service.create_new_post(db, post_data=post, user_id=current_user.id)
    return ApiResponse(data=post)


@router.put("/{id}", response_model=ApiResponse[PostUpdate])
async def update_post(
        id: Annotated[UUID, Path()],
        post_update: Annotated[PostUpdate, Form()],
        db: SessionDep,
        current_user: CurrentUserDep,
):
    post_updated = await post_service.update_post(db, id, post_update, current_user.id)
    return ApiResponse(success=True, data=post_updated)


@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_post(
        id: Annotated[UUID, Path()],
        db: SessionDep,
        current_user: CurrentUserDep,
):
    await post_service.delete_post(db, id, current_user.id)
    return ApiResponse(success=True, message="Post deleted")
