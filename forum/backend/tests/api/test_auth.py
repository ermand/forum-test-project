import pytest

@pytest.mark.asyncio
async def test_register(client):
    res = await client.post(
        "/api/auth/register",
        params={
            "username": "tester_new",
            "email": "test_new@test.com",
            "password": "Password123!",
        }
    )
    assert res.status_code == 201, f"Regjistrimi dështoi: {res.text}"


@pytest.mark.asyncio
async def test_login_token(client):
    # 1. Regjistrimi (Shtojmë email-in dhe kontrollojmë statusin)
    reg_res = await client.post(
        "/api/auth/register",
        params={
            "username": "tester_new",
            "email": "tester_new@example.com",  # Shto email-in
            "password": "Password123!",
        }
    )
    # Ky assert do të të tregojë nëse regjistrimi dështon me 422 apo 400
    assert reg_res.status_code == 201, f"Regjistrimi dështoi: {reg_res.text}"

    # 2. Login
    res = await client.post(
        "/api/auth/token",
        data={
            "grant_type": "password",
            "username": "tester_new",
            "password": "Password123!",
        }
    )

    assert res.status_code == 200, f"Login dështoi: {res.text}"