"""Validate docker-compose.yml structure for NAS deployment."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COMPOSE_FILE = ROOT / "docker-compose.yml"


def test_docker_compose_file_exists_and_has_required_services():
    assert COMPOSE_FILE.is_file()
    content = COMPOSE_FILE.read_text()
    assert "api:" in content
    assert "web:" in content
    assert "build: ./backend" in content
    assert "build: ./frontend" in content
    assert "SQLITE_PATH: /data/osintgraph.db" in content
    assert "osintgraph_data:" in content
    assert "service_healthy" in content
    assert "OSINTGRAPH_PORT" in content
