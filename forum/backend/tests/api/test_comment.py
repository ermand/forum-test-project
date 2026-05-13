import pytest


# =========================
# CREATE COMMENT
# =========================
@pytest.mark.asyncio
async def test_create_comment(client, auth_headers, test_posts):
    post1, _, _ = test_posts

    res = await client.post(
        f"/api/posts/{post1.id}/comments",
        data={
            "content": "Ky është një koment valid",
            "post_id": str(post1.id)
        },
        headers=auth_headers
    )
    body = res.json()
    assert res.status_code == 201, f"Gabim: {res.text}"
    assert body["success"] is True
    assert body["data"]["content"] == "Ky është një koment valid"
    assert str(body["data"]["post_id"]) == str(post1.id)


# =========================
# UPDATE COMMENT
# =========================
@pytest.mark.asyncio
async def test_update_comment(client, test_comments, auth_headers):
    comment1, *_ = test_comments

    result = await client.put(
        f"/api/comments/{comment1.id}",
        data={
            "content": "Updated Comment",
        },
        headers=auth_headers,
    )

    assert result.status_code == 200

    body = result.json()
    assert body["success"] is True
    assert body["data"]["content"] == "Updated Comment"


# =========================
# DELETE COMMENT
# =========================
@pytest.mark.asyncio
async def test_delete_comment(client, test_comments, auth_headers):
    comment1, *_ = test_comments

    result = await client.delete(
        f"/api/comments/{comment1.id}",
        headers=auth_headers,
    )

    assert result.status_code == 200

    body = result.json()
    assert body["success"] is True


# =========================
# GET COMMENTS BY POST
# =========================
@pytest.mark.asyncio
async def test_get_comments(client, test_posts):
    post1, _, _ = test_posts

    result = await client.get(
        f"/api/posts/{post1.id}/comments",
    )

    assert result.status_code == 200

    body = result.json()
    assert body["success"] is True
    assert "items" in body["data"]