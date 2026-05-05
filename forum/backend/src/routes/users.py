from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, Path
from core.auth.dependencies import CurrentUserDep
from core.db_connection.session import SessionDep
from src.schemas.user import UserResponse, UserProfileResponse
from src.services import user_service
from src.utils import ApiResponse, PaginationParams

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=ApiResponse[UserProfileResponse])
async def get_my_profile(db: SessionDep, current_user: CurrentUserDep, params: Annotated[PaginationParams, Query()]):
    profile_data = await user_service.get_user_profile(db, user_id=current_user.id, params=params
                                                       )
    return ApiResponse(data=profile_data)


@router.get("/{id}", response_model=ApiResponse[UserResponse])
async def get_user_by_id(id: Annotated[UUID, Path()], db: SessionDep):
    user = await user_service.get_user_by_id(db, user_id=id)

    return ApiResponse(
        success=True,
        message="User fetched successfully",
        data=user
    )
