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
