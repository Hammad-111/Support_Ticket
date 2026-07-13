async def test_signup(client):
    response = await client.post(
        "/auth/signup",
        json={"email": "user@test.com", "password": "123456"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "user@test.com"
    assert data["role"] == "user"


async def test_signup_duplicate_email(client):
    payload = {"email": "dup@test.com", "password": "123456"}
    await client.post("/auth/signup", json=payload)

    response = await client.post("/auth/signup", json=payload)
    assert response.status_code == 400


async def test_login(client):
    await client.post(
        "/auth/signup",
        json={"email": "login@test.com", "password": "123456"},
    )

    response = await client.post(
        "/auth/login",
        json={"email": "login@test.com", "password": "123456"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


async def test_login_wrong_password(client):
    await client.post(
        "/auth/signup",
        json={"email": "wrong@test.com", "password": "123456"},
    )

    response = await client.post(
        "/auth/login",
        json={"email": "wrong@test.com", "password": "wrongpass"},
    )
    assert response.status_code == 401


async def test_me(client):
    await client.post(
        "/auth/signup",
        json={"email": "me@test.com", "password": "123456"},
    )
    login = await client.post(
        "/auth/login",
        json={"email": "me@test.com", "password": "123456"},
    )
    token = login.json()["access_token"]

    response = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "me@test.com"
