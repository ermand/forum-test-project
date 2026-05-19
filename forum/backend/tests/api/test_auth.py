import pytest


@pytest.mark.asyncio
async def test_register_rejects_credentials_in_query_string(client):
    res = await client.post(
        "/api/auth/register",
        params={
            "username": "query_user",
            "email": "query@test.com",
            "password": "Password123!",
        },
    )

    assert res.status_code == 422


@pytest.mark.asyncio
async def test_register_normalizes_identity_and_rejects_duplicates(client):
    res = await client.post(
        "/api/auth/register",
        data={
            "username": "  Mixed_User  ",
            "email": "Mixed@Test.COM",
            "password": "Password123!",
        },
    )

    assert res.status_code == 201
    assert res.json()["username"] == "mixed_user"
    assert res.json()["email"] == "mixed@test.com"

    duplicate_username = await client.post(
        "/api/auth/register",
        data={
            "username": "MIXED_USER",
            "email": "other@test.com",
            "password": "Password123!",
        },
    )

    assert duplicate_username.status_code == 400

    duplicate_email = await client.post(
        "/api/auth/register",
        data={
            "username": "other_user",
            "email": "MIXED@test.com",
            "password": "Password123!",
        },
    )

    assert duplicate_email.status_code == 400


@pytest.mark.asyncio
async def test_refresh_token(client):
    await client.post(
        "/api/auth/register",
        data={
            "username": "refresh_user",
            "email": "refresh@test.com",
            "password": "Password123!",
        },
    )

    login_res = await client.post(
        "/api/auth/token",
        data={
            "grant_type": "password",
            "username": "refresh_user",
            "password": "Password123!",
        },
    )

    tokens = login_res.json()
    refresh_token = tokens["refresh_token"]

    res = await client.post(
        "/api/auth/token/refresh", data={"refresh_token": refresh_token}
    )

    assert res.status_code == 200


@pytest.mark.asyncio
async def test_logout(client):
    await client.post(
        "/api/auth/register",
        data={
            "username": "logout_user",
            "email": "logout@test.com",
            "password": "Password123!",
        },
    )

    login_res = await client.post(
        "/api/auth/token",
        data={
            "grant_type": "password",
            "username": "logout_user",
            "password": "Password123!",
        },
    )

    tokens = login_res.json()

    access_token = tokens["access_token"]

    res = await client.post(
        "/api/auth/logout", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert res.status_code == 200


@pytest.mark.asyncio
async def test_refresh_after_logout_should_fail(client):
    await client.post(
        "/api/auth/register",
        data={
            "username": "after_logout_user",
            "email": "afterlogout@test.com",
            "password": "Password123!",
        },
    )

    login_res = await client.post(
        "/api/auth/token",
        data={
            "grant_type": "password",
            "username": "after_logout_user",
            "password": "Password123!",
        },
    )

    tokens = login_res.json()

    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    await client.post(
        "/api/auth/logout", headers={"Authorization": f"Bearer {access_token}"}
    )

    refresh_res = await client.post(
        "/api/auth/token/refresh", data={"refresh_token": refresh_token}
    )

    assert refresh_res.status_code == 401
