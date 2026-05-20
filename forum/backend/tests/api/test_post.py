import pytest


@pytest.mark.asyncio
async def test_create_post(client, auth_headers):
    result = await client.post(
        "/api/posts/",
        data={
            "title": "Test Post",
            "content": "Test Content",
        },
        headers=auth_headers,
    )

    assert result.status_code == 201
    body = result.json()
    assert body["success"] is True
    assert body["data"]["title"] == "Test Post"


@pytest.mark.asyncio
async def test_update_post(client, test_posts, auth_headers):
    post1, _, _ = test_posts

    result = await client.put(
        f"/api/posts/{post1.id}",
        data={
            "title": "Updated Title",
            "content": "Updated Content",
        },
        headers=auth_headers,
    )

    assert result.status_code == 200
    assert result.json()["success"] is True
    assert result.json()["data"]["title"] == "Updated Title"


@pytest.mark.asyncio
async def test_delete_post(client, test_posts, auth_headers):
    post1, _, _ = test_posts

    result = await client.delete(f"/api/posts/{post1.id}", headers=auth_headers)
    assert result.status_code == 200
    assert result.json()["success"] is True


@pytest.mark.asyncio
async def test_get_posts(client, test_posts):
    result = await client.get(
        "/api/posts/",
    )
    assert result.status_code == 200
    assert result.json()["success"] is True
    assert len(result.json()["data"]["items"]) == len(test_posts)
    assert result.json()["data"]["meta"]["total_items"] == len(test_posts)


@pytest.mark.asyncio
async def test_get_post_by_id(client, test_posts):
    _, post2, _ = test_posts
    result = await client.get(
        f"/api/posts/{post2.id}",
    )
    assert result.status_code == 200
    assert result.json()["success"] is True
    assert result.json()["data"]["title"] == "Post 2"
    assert result.json()["data"]["content"] == "Content 2 i gjate mjaftueshem"
