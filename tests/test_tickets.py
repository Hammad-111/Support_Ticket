async def signup_and_login(client, email, password="123456", role="user"):
    await client.post(
        "/auth/signup",
        json={"email": email, "password": password, "role": role},
    )
    login = await client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    return login.json()["access_token"]


async def test_create_ticket(client):
    token = await signup_and_login(client, "ticket@test.com")

    response = await client.post(
        "/tickets",
        json={"title": "Help", "description": "App not working"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Help"
    assert data["status"] == "open"


async def test_list_own_tickets(client):
    token = await signup_and_login(client, "list@test.com")

    await client.post(
        "/tickets",
        json={"title": "Ticket 1", "description": "First"},
        headers={"Authorization": f"Bearer {token}"},
    )
    await client.post(
        "/tickets",
        json={"title": "Ticket 2", "description": "Second"},
        headers={"Authorization": f"Bearer {token}"},
    )

    response = await client.get(
        "/tickets",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert len(response.json()) == 2


async def test_cannot_see_others_ticket(client):
    token1 = await signup_and_login(client, "user1@test.com")
    token2 = await signup_and_login(client, "user2@test.com")

    created = await client.post(
        "/tickets",
        json={"title": "Private", "description": "Mine only"},
        headers={"Authorization": f"Bearer {token1}"},
    )
    ticket_id = created.json()["id"]

    response = await client.get(
        f"/tickets/{ticket_id}",
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert response.status_code == 403
