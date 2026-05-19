from typing import Annotated

from fastapi import APIRouter, Depends, Request, Form
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr

from core.rate_limit import limiter
from core.db_connection.session import SessionDep
from src.config.settings import SettingsDep
from src.schemas.token import Token
from src.schemas.user import UserCreate, UserResponse
from src.services import user_service, auth_service
from src.services.auth_service import issue_token_pair

from core.auth.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


def registration_form(
    username: Annotated[str, Form(...)],
    email: Annotated[EmailStr, Form(...)],
    password: Annotated[str, Form(...)],
) -> UserCreate:

    return UserCreate(username=username, email=email, password=password)


@router.post("/register", response_model=UserResponse, status_code=201)
@limiter.limit("10/minute")
async def register_user(
    request: Request,
    user_data: Annotated[UserCreate, Depends(registration_form)],
    db: SessionDep,
):
    return await auth_service.register_user_service(db, user_data, user_service)


@router.post("/token", response_model=Token)
@router.post("/login", response_model=Token, include_in_schema=False)
@limiter.limit("10/minute")
async def login_for_tokens(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: SessionDep,
    settings: SettingsDep,
):
    return await auth_service.login_user_service(
        db,
        form_data.username,
        form_data.password,
        user_service,
        issue_token_pair,
        settings,
    )


@router.post("/token/refresh", response_model=Token)
async def refresh_tokens(
    request: Request,
    db: SessionDep,
    settings: SettingsDep,
    refresh_token: str = Form(...),
):
    return await auth_service.refresh_token_service(
        db,
        refresh_token,
        settings,
    )


@router.post("/logout")
async def logout(
    request: Request,
    db: SessionDep,
    user=Depends(get_current_user),
):
    return await auth_service.logout_user_service(db, user)
