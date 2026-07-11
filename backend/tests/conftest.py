import asyncio
import os

os.environ.setdefault("SQLITE_PATH", "test_osintgraph_pytest.db")

import pytest


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    async def _init():
        from db.domain_client import domain_client
        await domain_client.init_schema()
        await domain_client.ensure_default_dossier()

    asyncio.run(_init())
    yield
    for f in ("test_osintgraph_pytest.db", "test_osintgraph_pytest.db-wal", "test_osintgraph_pytest.db-shm"):
        try:
            os.remove(f)
        except FileNotFoundError:
            pass
