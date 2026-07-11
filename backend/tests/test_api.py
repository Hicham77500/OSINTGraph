import pytest
from httpx import ASGITransport, AsyncClient

@pytest.fixture
async def client():
    from main import app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health(client):
    res = await client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["service"] == "OSINTGraph"


@pytest.mark.asyncio
async def test_transform_registry():
    from transforms.base import autodiscover, list_transforms
    autodiscover()
    transforms = list_transforms()
    names = {t["name"] for t in transforms}
    assert "dns_lookup" in names
    assert len(transforms) >= 6


@pytest.mark.asyncio
async def test_graph_crud(client):
    ws = "test_pytest_ws"
    payload = {
        "nodes": [{"id": "n1", "type": "domain", "label": "example.com", "properties": {}}],
        "edges": [],
    }
    res = await client.post(f"/graph/{ws}", json=payload)
    assert res.status_code == 200
    res = await client.get(f"/graph/{ws}")
    assert res.status_code == 200
    data = res.json()
    assert len(data["nodes"]) == 1
    assert data["nodes"][0]["label"] == "example.com"


@pytest.mark.asyncio
async def test_dossiers_api(client):
    res = await client.get("/api/v1/dossiers")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


@pytest.mark.asyncio
async def test_search_api(client):
    res = await client.get("/api/v1/search?q=test")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


@pytest.mark.asyncio
async def test_entity_update_and_delete(client):
    res = await client.post("/api/v1/dossiers", json={"name": "Entity CRUD Test"})
    assert res.status_code == 201
    dossier_id = res.json()["id"]

    res = await client.get(f"/api/v1/dossiers/{dossier_id}/carnets")
    notes_carnet = next(c for c in res.json() if c["notebook_type"] == "notes")

    res = await client.post(
        f"/api/v1/dossiers/{dossier_id}/entities",
        json={
            "entity_type": "CUSTOM",
            "label": "Original title",
            "carnet_id": notes_carnet["id"],
            "properties": {"title": "Original title", "content": "First body"},
        },
    )
    assert res.status_code == 201
    entity_id = res.json()["id"]

    res = await client.patch(
        f"/api/v1/entities/{entity_id}",
        json={
            "label": "Updated title",
            "properties": {"title": "Updated title", "content": "Updated body"},
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["label"] == "Updated title"
    assert data["properties"]["content"] == "Updated body"

    res = await client.delete(f"/api/v1/entities/{entity_id}")
    assert res.status_code == 200
    assert res.json()["ok"] is True

    res = await client.get(f"/api/v1/entities/{entity_id}")
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_dossier_soft_delete_restore_permanent(client):
    res = await client.post("/api/v1/dossiers", json={"name": "Trash Test Dossier"})
    assert res.status_code == 201
    dossier_id = res.json()["id"]

    res = await client.delete(f"/api/v1/dossiers/{dossier_id}")
    assert res.status_code == 200
    assert res.json()["deleted_at"] is not None

    res = await client.get("/api/v1/dossiers")
    ids = [d["id"] for d in res.json()]
    assert dossier_id not in ids

    res = await client.get("/api/v1/dossiers/trash")
    assert res.status_code == 200
    trash_ids = [d["id"] for d in res.json()]
    assert dossier_id in trash_ids

    res = await client.get(f"/api/v1/dossiers/{dossier_id}")
    assert res.status_code == 404

    res = await client.post(f"/api/v1/dossiers/{dossier_id}/restore")
    assert res.status_code == 200
    assert res.json()["deleted_at"] is None

    res = await client.get(f"/api/v1/dossiers/{dossier_id}")
    assert res.status_code == 200

    res = await client.delete(f"/api/v1/dossiers/{dossier_id}")
    assert res.status_code == 200

    res = await client.delete(f"/api/v1/dossiers/{dossier_id}/permanent")
    assert res.status_code == 200
    assert res.json()["ok"] is True

    res = await client.get("/api/v1/dossiers/trash")
    trash_ids = [d["id"] for d in res.json()]
    assert dossier_id not in trash_ids
