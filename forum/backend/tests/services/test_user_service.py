import pytest
from src.utils.schemas import PaginationParams
from src.services import user_service


@pytest.mark.asyncio
async def test_get_user(db,auth_user):
    params = PaginationParams(page=1, page_size=10)

    result = await user_service.get_user_profile(db,auth_user.id, params)

    assert result is not None
    assert result["user_info"].id == auth_user.id
    assert result["user_info"].email == auth_user.email


@pytest.mark.asyncio
async def test_get_user_by_email(db,auth_user):
    result = await user_service.get_user_by_email(db,auth_user.email)

    assert result is not None
    assert result.id ==auth_user.id
    assert result.email ==auth_user.email


@pytest.mark.asyncio
async def test_get_user_by_username(db,auth_user):
    result = await user_service.get_user_by_username(db, auth_user.username)

    assert result is not None
    assert result.id == auth_user.id
    assert result.username == auth_user.username
    assert result.email == auth_user.email


@pytest.mark.asyncio
async def test_get_user_by_id(db,auth_user):
    result = await user_service.get_user_by_id(db, auth_user.id)

    assert result is not None
    assert result.id == auth_user.id
    assert result.username == auth_user.username
    assert result.email == auth_user.email

