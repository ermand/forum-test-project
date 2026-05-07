import pytest
import pytest_asyncio

from src.schemas.posts import PostCreate, PostUpdate
from src.services import post_service
from src.utils import PaginationParams


@pytest.mark.asyncio
async def test_create_post(db,auth_user):
    post_data = PostCreate(
        title="Test Post",
        content="Test Post"
    )

    result = await post_service.create_new_post(db, post_data=post_data, user_id=auth_user.id)

    assert result is not None
    assert result.title == post_data.title
    assert result.content == post_data.content
    assert result.user_id == auth_user.id


@pytest.mark.asyncio
async def test_get_posts(db, test_posts):
    params = PaginationParams(page=1, page_size=10)

    result = await post_service.get_posts(db, params)

    assert result is not None
    assert len(result.items) == 3


@pytest.mark.asyncio
async def test_update_post(db, auth_user, test_posts):
    post1, post2, post3 = test_posts

    post_data = PostUpdate(
        content="Test Test",
    )

    result = await post_service.update_post(db, post_id=post2.id, post_update=post_data, user_id=auth_user.id)
    assert result is not None
    assert result.content == "Test Test"


@pytest.mark.asyncio
async def test_get_post_by_id(db, auth_user, test_posts, test_comments):
    post1, post2, post3 = test_posts

    result = await post_service.get_post(db, post_id=post2.id)

    assert result is not None
    assert result.title == "Post 2"
    assert result.content == "Content 2"
    assert result.id == post2.id
    assert result.user_id == auth_user.id
    assert len(result.comments) == 1


@pytest.mark.asyncio
async def test_delete_post(db, auth_user, test_posts):
    post1, post2, post3 = test_posts

    result = await post_service.delete_post(db, post_id=post2.id, user_id=auth_user.id)

    assert result is True
