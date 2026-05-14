import pytest

from src.schemas.comment import CommentCreate, CommentUpdate
from src.services import comment_service
from src.utils import PaginationParams

@pytest.mark.asyncio
async def test_create_comment(db, auth_user, test_posts):
    post1, post2, post3 = test_posts

    comment = CommentCreate(
        content="Test",
        post_id=post1.id
    )

    result = await comment_service.comment_create(
        db,
        comment_data=comment,
        user_id=auth_user.id
    )

    assert result is not None
    assert result.content == "Test"
    assert result.post_id == post1.id
    assert result.user_id == auth_user.id

@pytest.mark.asyncio
async def test_get_comments_by_post_id(db, test_posts, test_comments):
    post1, post2, post3 = test_posts

    params = PaginationParams(page=1, page_size=10)

    result = await comment_service.get_post_comments(db, post_id=post1.id, params=params)

    assert result is not None
    assert len(result.items) == 2

    for comment in result.items:
        assert comment.post_id == post1.id


@pytest.mark.asyncio
async def test_update_comment(db, auth_user, test_posts, test_comments):
    post1, post2, post3 = test_posts
    c1, c2, c3, c4, c5 = test_comments

    comment = CommentUpdate(
        content="TestUpdate",
    )
    result = await comment_service.update_post_comment(db, comment_data=comment, user_id=auth_user.id, comment_id=c2.id)

    assert result is not None
    assert result.content == "TestUpdate"
    assert result.post_id == post1.id
    assert result.user_id == auth_user.id


@pytest.mark.asyncio
async def test_delete_comment(db, auth_user, test_comments):
    c1, c2, c3, c4, c5 = test_comments

    result = await comment_service.delete_post_comment(db, comment_id=c2.id, user_id=auth_user.id)

    assert result is True
