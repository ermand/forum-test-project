import pytest
import pytest_asyncio

from core.auth.jwt import decode_access_token


@pytest.mark.asyncio
async def test_register(client):
    res = await client.post("/api/auth/register",
        data={
            "username": "tester",
            "email": "test@test.com",
            "password": "password123",
        }
    )

    assert res.status_code == 201
    body = res.json()

    assert body["username"] == "tester"
    assert body["email"] == "test@test.com"
    assert "id" in body


@pytest.mark.asyncio
async def test_login_token(client):
    await client.post(
        "/api/auth/register",
        data={
            "username": "tester",
            "email": "test@test.com",
            "password": "password123",
        },
    )

    res = await client.post( "/api/auth/token",
        data={
            "username": "test@test.com",
            "password": "password123",
        },
    )

    assert res.status_code == 200
    body = res.json()

    assert "access_token" in body
    assert "refresh_token" in body

    payload = decode_access_token(body["access_token"])
    assert payload["sub"] == "tester"
    assert payload["typ"] == "access"

@pytest.mark.asyncio
async def test_get_user(client, auth_headers):
    result = await client.get(
        "/api/users/me",
        headers=auth_headers,
    )
    assert result.status_code == 200
    body = result.json()
    assert body["data"]["user_info"]["username"] == "tester"
    assert body["data"]["user_info"]["email"] == "test@test.com"

@pytest.mark.asyncio
async def test_get_user_by_id(client, auth_user):
    result = await client.get(
        f"/api/users/{auth_user.id}",
    )

    assert result.status_code == 200
    body = result.json()

    assert body["data"]["username"] == "tester"
    assert body["data"]["email"] == "test@test.com"