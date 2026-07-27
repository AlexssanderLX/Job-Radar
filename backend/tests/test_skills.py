import pytest


@pytest.mark.asyncio
async def test_create_skill(client):
    resp = await client.post("/api/skills", json={
        "name": "Python",
        "category": "language",
        "aliases": ["python3", "py"],
        "active": True,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Python"
    assert data["category"] == "language"


@pytest.mark.asyncio
async def test_list_skills(client):
    await client.post("/api/skills", json={"name": "Docker", "category": "devops"})
    await client.post("/api/skills", json={"name": "Terraform", "category": "iac"})

    resp = await client.get("/api/skills")
    assert resp.status_code == 200
    assert len(resp.json()) >= 2


@pytest.mark.asyncio
async def test_get_skill(client):
    create_resp = await client.post("/api/skills", json={"name": "Kubernetes"})
    skill_id = create_resp.json()["id"]

    resp = await client.get(f"/api/skills/{skill_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Kubernetes"


@pytest.mark.asyncio
async def test_update_skill(client):
    create_resp = await client.post("/api/skills", json={"name": "Old Skill"})
    skill_id = create_resp.json()["id"]

    resp = await client.patch(f"/api/skills/{skill_id}", json={"name": "Updated Skill", "active": False})
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated Skill"
    assert resp.json()["active"] is False


@pytest.mark.asyncio
async def test_delete_skill(client):
    create_resp = await client.post("/api/skills", json={"name": "Ephemeral Skill"})
    skill_id = create_resp.json()["id"]

    resp = await client.delete(f"/api/skills/{skill_id}")
    assert resp.status_code == 204

    get_resp = await client.get(f"/api/skills/{skill_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_duplicate_skill_rejected(client):
    await client.post("/api/skills", json={"name": "Unique Skill"})
    resp = await client.post("/api/skills", json={"name": "Unique Skill"})
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_filter_skills_by_category(client):
    await client.post("/api/skills", json={"name": "AWS", "category": "cloud"})
    await client.post("/api/skills", json={"name": "React", "category": "frontend"})

    resp = await client.get("/api/skills?category=cloud")
    assert resp.status_code == 200
    names = [s["name"] for s in resp.json()]
    assert "AWS" in names
    assert "React" not in names
