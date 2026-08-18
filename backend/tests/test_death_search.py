"""Tests for death_search plugin helpers and query logic."""
import os
from pathlib import Path

import duckdb
import pytest

from plugins.death_search.plugin import (
    DeathSearchPlugin,
    _query_deaths_sync,
    partition_letter,
    resolve_parquet_path,
)
from plugins.helpers import format_date_yyyymmdd, parse_person_label


FIXTURES = Path(__file__).parent / "fixtures"
SAMPLE_PARQUET = FIXTURES / "death_sample.parquet"


@pytest.fixture(scope="module", autouse=True)
def sample_parquet():
    FIXTURES.mkdir(exist_ok=True)
    con = duckdb.connect()
    con.execute("""
        CREATE TABLE death_sample AS SELECT * FROM (VALUES
            ('DUPONT', 'JEAN,PIERRE', 'M', '19500315', '75056', 'PARIS', NULL, '20200110', '75056', '123'),
            ('DUPONT', 'MARIE', 'F', '19620401', '69123', 'LYON', NULL, '20180622', '69123', '456'),
            ('MARTIN', 'PAUL', 'M', '19400101', '13055', 'MARSEILLE', NULL, '19990707', '13055', '789')
        ) AS t(nom, prenoms, sexe, date_naissance, code_insee_naissance,
               commune_naissance, pays_naissance, date_deces, code_insee_deces, numero_acte_deces)
    """)
    con.execute(f"COPY death_sample TO '{SAMPLE_PARQUET}' (FORMAT PARQUET)")
    con.close()
    yield
    if SAMPLE_PARQUET.exists():
        SAMPLE_PARQUET.unlink()


def test_parse_person_label_french_style():
    nom, prenom = parse_person_label("Jean-Pierre DUPONT")
    assert nom == "DUPONT"
    assert prenom == "Jean-Pierre"


def test_parse_person_label_comma():
    nom, prenom = parse_person_label("DUPONT, Jean")
    assert nom == "DUPONT"
    assert prenom == "Jean"


def test_format_date():
    assert format_date_yyyymmdd("19500315") == "15/03/1950"


def test_partition_letter():
    assert partition_letter("DUPONT") == "D"
    assert partition_letter("'T HOOFT") == "AUTRE"


def test_resolve_parquet_path_partitioned():
    path = resolve_parquet_path("/data/parts", "DUPONT")
    assert path == "/data/parts/lettre=D/data.parquet"


@pytest.mark.asyncio
async def test_plugin_requires_data_config():
    plugin = DeathSearchPlugin()
    from plugins.base import PluginContext
    from unittest.mock import MagicMock

    ctx = PluginContext(
        entity=MagicMock(label="Jean DUPONT"),
        api_manager=MagicMock(),
        logger=MagicMock(),
        config={},
    )
    old_path = os.environ.pop("DEATH_RECORDS_PATH", None)
    old_url = os.environ.pop("DEATH_RECORDS_BASE_URL", None)
    try:
        result = await plugin.run(ctx)
        assert result["nodes"] == []
        assert any("Données non configurées" in line for line in result["log"])
    finally:
        if old_path:
            os.environ["DEATH_RECORDS_PATH"] = old_path
        if old_url:
            os.environ["DEATH_RECORDS_BASE_URL"] = old_url


def test_query_deaths_sync_filters():
    rows, log = _query_deaths_sync(
        str(SAMPLE_PARQUET),
        "DUPONT",
        "JEAN",
        None,
        None,
        None,
        None,
        10,
    )
    assert len(rows) == 1
    assert rows[0]["nom"] == "DUPONT"
    assert "JEAN" in rows[0]["prenoms"]
    assert any("1 enregistrement" in line for line in log)


def test_query_deaths_sync_commune_filter():
    rows, _ = _query_deaths_sync(
        str(SAMPLE_PARQUET),
        "DUPONT",
        None,
        None,
        None,
        "lyon",
        None,
        10,
    )
    assert len(rows) == 1
    assert rows[0]["commune_naissance"] == "LYON"


@pytest.mark.asyncio
async def test_plugin_run_with_local_parquet():
    plugin = DeathSearchPlugin()
    from plugins.base import PluginContext
    from unittest.mock import MagicMock

    ctx = PluginContext(
        entity=MagicMock(label="DUPONT"),
        api_manager=MagicMock(),
        logger=MagicMock(),
        config={"data_path": str(SAMPLE_PARQUET), "prenom": "MARIE"},
    )
    result = await plugin.run(ctx)
    assert len(result["nodes"]) >= 1
    assert result["nodes"][0]["type"] == "PERSON"
    assert result["observations"]
    assert result["observations"][0]["status"] == "UNVERIFIED"
