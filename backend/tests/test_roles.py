import pytest


@pytest.mark.asyncio
async def test_create_role(client):
    resp = await client.post("/api/roles", json={
        "name": "Test Role",
        "category": "development",
        "aliases": ["test", "testing"],
        "active": True,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Test Role"
    assert data["category"] == "development"
    assert "test" in data["aliases"]


@pytest.mark.asyncio
async def test_list_roles(client):
    await client.post("/api/roles", json={"name": "Role A", "active": True})
    await client.post("/api/roles", json={"name": "Role B", "active": False})

    resp = await client.get("/api/roles")
    assert resp.status_code == 200
    assert len(resp.json()) >= 2


@pytest.mark.asyncio
async def test_get_role(client):
    create_resp = await client.post("/api/roles", json={"name": "Specific Role", "aliases": ["sr"]})
    role_id = create_resp.json()["id"]

    resp = await client.get(f"/api/roles/{role_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Specific Role"


@pytest.mark.asyncio
async def test_update_role(client):
    create_resp = await client.post("/api/roles", json={"name": "Old Name"})
    role_id = create_resp.json()["id"]

    resp = await client.patch(f"/api/roles/{role_id}", json={"name": "New Name", "active": False})
    assert resp.status_code == 200
    assert resp.json()["name"] == "New Name"
    assert resp.json()["active"] is False


@pytest.mark.asyncio
async def test_delete_role(client):
    create_resp = await client.post("/api/roles", json={"name": "To Delete"})
    role_id = create_resp.json()["id"]

    resp = await client.delete(f"/api/roles/{role_id}")
    assert resp.status_code == 204

    get_resp = await client.get(f"/api/roles/{role_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_duplicate_role_rejected(client):
    await client.post("/api/roles", json={"name": "Unique Role"})
    resp = await client.post("/api/roles", json={"name": "Unique Role"})
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_filter_roles_by_active(client):
    await client.post("/api/roles", json={"name": "Active Role", "active": True})
    await client.post("/api/roles", json={"name": "Inactive Role", "active": False})

    resp = await client.get("/api/roles?active=true")
    assert resp.status_code == 200
    names = [r["name"] for r in resp.json()]
    assert "Active Role" in names
    assert "Inactive Role" not in names
