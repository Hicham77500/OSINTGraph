#!/usr/bin/env python3
"""
One-time demo seed for README screenshots — dossier TEST only.

Populates realistic French OSINT-style fake data (persons, social accounts,
organizations, notes, relations, observations, legacy graph blob).
Idempotent: skips if marker entity exists unless --force is passed.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

# Run from backend/ so imports and default SQLITE_PATH resolve correctly.
BACKEND_DIR = Path(__file__).resolve().parent.parent
os.chdir(BACKEND_DIR)
sys.path.insert(0, str(BACKEND_DIR))

from dotenv import load_dotenv

load_dotenv()

from db.domain_client import domain_client
from db.sqlite_client import sqlite_client
from models.domain import (
    CollectionMethod,
    ConfidenceStatus,
    DossierCreate,
    EntityCreate,
    EntityUpdate,
    RelationCreate,
    RelationType,
    new_id,
)

DOSSIER_NAMES = ("TEST", "Test")
MARKER_LABEL = "__osintgraph_demo_seed_v1__"
SEED_ACTOR = "demo-seed"


def _entity_type_to_node_type(entity_type: str) -> str:
    etype_map = {
        "PERSON": "person",
        "ORGANIZATION": "organization",
        "USERNAME": "username",
        "SOCIAL_ACCOUNT": "username",
        "EMAIL": "email",
        "DOMAIN": "domain",
        "CUSTOM": "person",
    }
    return etype_map.get(entity_type, "username")


def _relation_to_edge_type(relation_type: str) -> str:
    if relation_type == RelationType.USES.value:
        return "uses"
    if relation_type in (RelationType.OWNS.value, RelationType.CREATED.value):
        return "owns"
    if relation_type == RelationType.RESOLVES_TO.value:
        return "resolves_to"
    return "linked_to"


async def find_test_dossier() -> dict | None:
    dossiers = await domain_client.list_dossiers()
    for d in dossiers:
        if d.name.strip().lower() == "test":
            return {
                "id": d.id,
                "name": d.name,
                "workspace_id": d.workspace_id,
                "description": d.description,
            }
    return None


async def ensure_test_dossier() -> dict:
    existing = await find_test_dossier()
    if existing:
        return existing
    created = await domain_client.create_dossier(
        DossierCreate(
            name="TEST",
            description="Dossier démo — captures README (données fictives)",
        ),
        workspace_id=None,
        actor=SEED_ACTOR,
    )
    return {
        "id": created.id,
        "name": created.name,
        "workspace_id": created.workspace_id,
        "description": created.description,
    }


async def is_already_seeded(dossier_id: str) -> bool:
    async with domain_client._session() as db:
        async with db.execute(
            "SELECT 1 FROM entities WHERE dossier_id = ? AND label = ? LIMIT 1",
            (dossier_id, MARKER_LABEL),
        ) as cur:
            return (await cur.fetchone()) is not None


async def clear_dossier_seed_data(dossier_id: str, workspace_key: str) -> None:
    async with domain_client._session() as db:
        await db.execute("DELETE FROM relations WHERE dossier_id = ?", (dossier_id,))
        await db.execute("DELETE FROM entities WHERE dossier_id = ?", (dossier_id,))
        await db.commit()
    await sqlite_client.save_graph(workspace_key, {"nodes": [], "edges": []})


async def carnet_map(dossier_id: str) -> dict[str, str]:
    carnets = await domain_client.list_carnets(dossier_id)
    return {c.notebook_type: c.id for c in carnets}


async def add_timed_observation(
    entity_id: str,
    *,
    platform: str,
    collection_method: CollectionMethod,
    content: dict,
    confidence: float,
    status: ConfidenceStatus,
    observed_at: str,
    url: str | None = None,
) -> str:
    """Like add_observation but with explicit observed_at for chronologie screenshots."""
    sid = new_id()
    oid = new_id()
    async with domain_client._session() as db:
        await db.execute(
            """INSERT INTO sources (id, entity_id, platform, url, collection_method, collected_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (sid, entity_id, platform, url, collection_method.value, observed_at),
        )
        await db.execute(
            """INSERT INTO observations
               (id, source_id, entity_id, content, observed_at, confidence, status)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                oid,
                sid,
                entity_id,
                json.dumps(content),
                observed_at,
                confidence,
                status.value,
            ),
        )
        await db.commit()
    return oid


async def seed(force: bool) -> dict:
    await domain_client.init_schema()
    dossier = await ensure_test_dossier()
    dossier_id = dossier["id"]
    workspace_key = dossier["workspace_id"] or dossier_id

    if await is_already_seeded(dossier_id):
        if not force:
            stats = await domain_client._dossier_stats(dossier_id)
            return {
                "skipped": True,
                "dossier_id": dossier_id,
                "workspace_key": workspace_key,
                "stats": stats,
            }
        await clear_dossier_seed_data(dossier_id, workspace_key)

    carnets = await carnet_map(dossier_id)
    c_personnes = carnets["personnes"]
    c_reseaux = carnets["reseaux_sociaux"]
    c_entreprises = carnets["entreprises"]
    c_chrono = carnets["chronologie"]
    c_notes = carnets["notes"]

    counts = {
        "persons": 0,
        "accounts": 0,
        "organizations": 0,
        "relations": 0,
        "notes": 0,
        "timeline_events": 0,
        "observations_extra": 0,
        "graph_nodes": 0,
        "graph_edges": 0,
    }

    marker = await domain_client.create_entity(
        dossier_id,
        EntityCreate(
            entity_type="CUSTOM",
            label=MARKER_LABEL,
            carnet_id=c_notes,
            properties={"hidden": True, "demo_seed": True},
            confidence=1.0,
            status=ConfidenceStatus.CONFIRMED,
        ),
        actor=SEED_ACTOR,
    )

    persons_spec = [
        {
            "label": "Camille Renard",
            "status": ConfidenceStatus.LIKELY,
            "confidence": 0.82,
            "props": {
                "ville": "Lyon",
                "role": "Analyste OSINT",
                "naissance": "1991",
            },
        },
        {
            "label": "Lucas Moreau",
            "status": ConfidenceStatus.CONFIRMED,
            "confidence": 0.91,
            "props": {"ville": "Villeurbanne", "role": "Développeur backend"},
        },
        {
            "label": "Inès Dubois",
            "status": ConfidenceStatus.LIKELY,
            "confidence": 0.76,
            "props": {"ville": "Lyon", "activite": "Community manager"},
        },
        {
            "label": "Mehdi Benali",
            "status": ConfidenceStatus.UNVERIFIED,
            "confidence": 0.55,
            "props": {"ville": "Grenoble", "alias_public": "mb_osint"},
        },
    ]

    person_ids: dict[str, str] = {}
    for spec in persons_spec:
        ent = await domain_client.create_entity(
            dossier_id,
            EntityCreate(
                entity_type="PERSON",
                label=spec["label"],
                carnet_id=c_personnes,
                properties=spec["props"],
                confidence=spec["confidence"],
                status=spec["status"],
            ),
            actor=SEED_ACTOR,
        )
        person_ids[spec["label"]] = ent.id
        counts["persons"] += 1

    orgs_spec = [
        {
            "label": "Novatech Solutions SAS",
            "status": ConfidenceStatus.CONFIRMED,
            "confidence": 0.88,
            "props": {"siret": "952 418 337 00019", "ville": "Lyon 3e", "secteur": "Cybersécurité"},
        },
        {
            "label": "Association Café Numérique Lyon",
            "status": ConfidenceStatus.LIKELY,
            "confidence": 0.7,
            "props": {"type": "Association loi 1901", "ville": "Lyon"},
        },
    ]

    org_ids: dict[str, str] = {}
    for spec in orgs_spec:
        ent = await domain_client.create_entity(
            dossier_id,
            EntityCreate(
                entity_type="ORGANIZATION",
                label=spec["label"],
                carnet_id=c_entreprises,
                properties=spec["props"],
                confidence=spec["confidence"],
                status=spec["status"],
            ),
            actor=SEED_ACTOR,
        )
        org_ids[spec["label"]] = ent.id
        counts["organizations"] += 1

    social_spec = [
        {
            "label": "@camille.osint",
            "etype": "SOCIAL_ACCOUNT",
            "props": {
                "platform": "Instagram",
                "handle": "camille.osint",
                "url": "https://instagram.com/camille.osint",
            },
            "status": ConfidenceStatus.CONFIRMED,
            "confidence": 0.86,
        },
        {
            "label": "@lmoreau_dev",
            "etype": "USERNAME",
            "props": {
                "platform": "X",
                "handle": "lmoreau_dev",
                "url": "https://x.com/lmoreau_dev",
            },
            "status": ConfidenceStatus.LIKELY,
            "confidence": 0.79,
        },
        {
            "label": "@ines.lyon",
            "etype": "SOCIAL_ACCOUNT",
            "props": {
                "platform": "TikTok",
                "handle": "ines.lyon",
                "url": "https://tiktok.com/@ines.lyon",
            },
            "status": ConfidenceStatus.LIKELY,
            "confidence": 0.74,
        },
        {
            "label": "novatech-lyon",
            "etype": "SOCIAL_ACCOUNT",
            "props": {
                "platform": "LinkedIn",
                "handle": "novatech-lyon",
                "url": "https://www.linkedin.com/company/novatech-lyon",
            },
            "status": ConfidenceStatus.CONFIRMED,
            "confidence": 0.9,
        },
    ]

    social_ids: dict[str, str] = {}
    for spec in social_spec:
        ent = await domain_client.create_entity(
            dossier_id,
            EntityCreate(
                entity_type=spec["etype"],
                label=spec["label"],
                carnet_id=c_reseaux,
                properties=spec["props"],
                confidence=spec["confidence"],
                status=spec["status"],
            ),
            actor=SEED_ACTOR,
        )
        social_ids[spec["label"]] = ent.id
        counts["accounts"] += 1
        await add_timed_observation(
            ent.id,
            platform=spec["props"]["platform"].lower(),
            collection_method=CollectionMethod.PUBLIC_SEARCH,
            content={
                "summary": f"Profil public {spec['props']['platform']} repéré",
                "handle": spec["props"]["handle"],
            },
            confidence=spec["confidence"],
            status=spec["status"],
            observed_at="2026-06-12 14:30:00",
            url=spec["props"].get("url"),
        )
        counts["observations_extra"] += 1

    notes_spec = [
        {
            "title": "Hypothèse — lien Novatech / événement Lyon",
            "content": (
                "Camille et Lucas partagent le même employeur sur LinkedIn. "
                "Le compte TikTok @ines.lyon mentionne un meetup « Café Numérique » "
                "le 15/03 — à recouper avec l'association."
            ),
        },
        {
            "title": "Piste Mehdi Benali",
            "content": (
                "Handle « mb_osint » vu en commentaire sur un post X de @lmoreau_dev. "
                "Confiance faible : pseudonyme commun, pas de confirmation hors plateforme."
            ),
        },
        {
            "title": "Checklist avant restitution",
            "content": (
                "1. Vérifier pages légales Novatech\n"
                "2. Archiver captures Instagram (horodatées)\n"
                "3. Documenter statut LIKELY vs CONFIRMED dans le rapport"
            ),
        },
    ]

    for note in notes_spec:
        await domain_client.create_entity(
            dossier_id,
            EntityCreate(
                entity_type="CUSTOM",
                label=note["title"],
                carnet_id=c_notes,
                properties={"title": note["title"], "content": note["content"]},
                confidence=0.65,
                status=ConfidenceStatus.POSSIBLE,
            ),
            actor=SEED_ACTOR,
        )
        counts["notes"] += 1

    timeline_spec = [
        {
            "label": "2026-03-15 — Meetup Café Numérique",
            "at": "2026-03-15 19:00:00",
            "platform": "tiktok",
            "summary": "Story @ines.lyon : affiche événement associative à Lyon",
            "status": ConfidenceStatus.LIKELY,
            "confidence": 0.72,
        },
        {
            "label": "2026-04-02 — Publication LinkedIn Novatech",
            "at": "2026-04-02 09:15:00",
            "platform": "linkedin",
            "summary": "Post recrutement « analyste threat intel » — tag ville Lyon",
            "status": ConfidenceStatus.CONFIRMED,
            "confidence": 0.9,
        },
        {
            "label": "2026-04-18 — Interaction X",
            "at": "2026-04-18 22:40:00",
            "platform": "x",
            "summary": "@lmoreau_dev répond à @mb_osint sur un thread sécurité web",
            "status": ConfidenceStatus.UNVERIFIED,
            "confidence": 0.58,
        },
        {
            "label": "2026-05-06 — Recoupement Instagram",
            "at": "2026-05-06 11:05:00",
            "platform": "instagram",
            "summary": "Photo géotaggée Lyon Part-Dieu — compte @camille.osint",
            "status": ConfidenceStatus.LIKELY,
            "confidence": 0.8,
        },
        {
            "label": "2026-06-01 — Synthèse analyste",
            "at": "2026-06-01 16:20:00",
            "platform": "manual",
            "summary": "Cluster personnes / orgs / comptes validé pour graphe de démonstration",
            "status": ConfidenceStatus.CONFIRMED,
            "confidence": 0.95,
        },
    ]

    for event in timeline_spec:
        ent = await domain_client.create_entity(
            dossier_id,
            EntityCreate(
                entity_type="EVENT",
                label=event["label"],
                carnet_id=c_chrono,
                properties={"kind": "timeline_marker"},
                confidence=event["confidence"],
                status=event["status"],
            ),
            actor=SEED_ACTOR,
        )
        counts["timeline_events"] += 1
        await add_timed_observation(
            ent.id,
            platform=event["platform"],
            collection_method=CollectionMethod.MANUAL
            if event["platform"] == "manual"
            else CollectionMethod.PUBLIC_SEARCH,
            content={"summary": event["summary"], "value": event["summary"]},
            confidence=event["confidence"],
            status=event["status"],
            observed_at=event["at"],
        )
        counts["observations_extra"] += 1

    relations_spec = [
        (person_ids["Camille Renard"], person_ids["Lucas Moreau"], RelationType.KNOWS, 0.77, ConfidenceStatus.LIKELY),
        (person_ids["Mehdi Benali"], person_ids["Inès Dubois"], RelationType.KNOWS, 0.52, ConfidenceStatus.UNVERIFIED),
        (person_ids["Camille Renard"], social_ids["@camille.osint"], RelationType.USES, 0.86, ConfidenceStatus.CONFIRMED),
        (person_ids["Lucas Moreau"], social_ids["@lmoreau_dev"], RelationType.USES, 0.81, ConfidenceStatus.LIKELY),
        (person_ids["Inès Dubois"], social_ids["@ines.lyon"], RelationType.USES, 0.78, ConfidenceStatus.LIKELY),
        (person_ids["Lucas Moreau"], org_ids["Novatech Solutions SAS"], RelationType.WORKS_AT, 0.9, ConfidenceStatus.CONFIRMED),
        (person_ids["Camille Renard"], org_ids["Novatech Solutions SAS"], RelationType.WORKS_AT, 0.7, ConfidenceStatus.LIKELY),
        (person_ids["Inès Dubois"], org_ids["Association Café Numérique Lyon"], RelationType.MEMBER_OF, 0.68, ConfidenceStatus.LIKELY),
        (org_ids["Novatech Solutions SAS"], social_ids["novatech-lyon"], RelationType.OWNS, 0.92, ConfidenceStatus.CONFIRMED),
    ]

    relation_rows: list[tuple[str, str, str, float, str]] = []
    for src, tgt, rtype, conf, status in relations_spec:
        rel = await domain_client.create_relation(
            dossier_id,
            RelationCreate(
                source_entity_id=src,
                target_entity_id=tgt,
                relation_type=rtype,
                confidence=conf,
                status=status,
            ),
            actor=SEED_ACTOR,
        )
        relation_rows.append((rel.id, src, tgt, conf, rtype.value))
        counts["relations"] += 1

    # Extra dated observations on persons for person view / search richness.
    await add_timed_observation(
        person_ids["Camille Renard"],
        platform="linkedin",
        collection_method=CollectionMethod.PUBLIC_SEARCH,
        content={"summary": "Profil public — expérience « Novatech Solutions »"},
        confidence=0.84,
        status=ConfidenceStatus.LIKELY,
        observed_at="2026-05-20 10:00:00",
        url="https://www.linkedin.com/in/camille-renard-demo",
    )
    counts["observations_extra"] += 1

    # Legacy graph blob (workspace key = workspace_id or dossier id).
    all_entities = await domain_client.list_entities(dossier_id)
    seed_entities = [e for e in all_entities if e.id != marker.id and e.label != MARKER_LABEL]

    nodes = []
    for e in seed_entities:
        if e.entity_type == "EVENT":
            continue
        nodes.append(
            {
                "id": e.id,
                "type": _entity_type_to_node_type(e.entity_type),
                "label": e.label,
                "properties": {k: str(v) for k, v in e.properties.items()},
                "metadata": {
                    "source": "demo-seed",
                    "confidence": int(e.confidence * 100),
                },
            }
        )

    edges = []
    for rel_id, src, tgt, conf, rtype in relation_rows:
        edges.append(
            {
                "id": rel_id,
                "source": src,
                "target": tgt,
                "type": _relation_to_edge_type(rtype),
                "label": rtype.replace("_", " ").title(),
                "properties": {"confidence": str(int(conf * 100))},
            }
        )

    await sqlite_client.save_graph(workspace_key, {"nodes": nodes, "edges": edges})
    counts["graph_nodes"] = len(nodes)
    counts["graph_edges"] = len(edges)

    stats = await domain_client._dossier_stats(dossier_id)
    return {
        "skipped": False,
        "dossier_id": dossier_id,
        "dossier_name": dossier["name"],
        "workspace_key": workspace_key,
        "stats": stats,
        "counts": counts,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed demo data into dossier TEST only.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Delete existing TEST seed data and re-seed",
    )
    args = parser.parse_args()
    result = asyncio.run(seed(force=args.force))

    if result.get("skipped"):
        print("Seed skipped: dossier TEST already contains demo data.")
        print(f"  dossier_id: {result['dossier_id']}")
        print(f"  stats: {result['stats']}")
        print("  Re-run with --force to replace.")
        return

    print("Demo seed completed for dossier TEST.")
    print(f"  dossier_id:   {result['dossier_id']}")
    print(f"  dossier_name: {result['dossier_name']}")
    print(f"  workspace_key (graph): {result['workspace_key']}")
    print(f"  hub stats:    {result['stats']}")
    print(f"  seeded:       {result['counts']}")
    print()
    print("Re-run:")
    print("  cd backend && .venv/bin/python scripts/seed_test_dossier.py")
    print("  cd backend && .venv/bin/python scripts/seed_test_dossier.py --force")


if __name__ == "__main__":
    main()
