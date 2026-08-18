"""Death Records Search — INSEE décès (data.gouv.fr), inspired by arbre-local."""
from __future__ import annotations

import asyncio
import os
import re
import unicodedata
from typing import Any

from plugins.base import PluginContext, TransformPlugin
from plugins.helpers import build_observation, format_date_yyyymmdd, parse_person_label

MAX_RESULTS_DEFAULT = 50
MAX_RESULTS_HARD = 100
DATA_SOURCE = "insee_deces"
DATA_ATTRIBUTION = "INSEE / data.gouv.fr — Licence Ouverte 2.0"


def normalize_name(name: str) -> str:
    """Uppercase and strip accents for INSEE name matching."""
    nfkd = unicodedata.normalize("NFKD", name)
    ascii_name = "".join(c for c in nfkd if not unicodedata.combining(c))
    return ascii_name.upper().strip()


def partition_letter(nom: str) -> str:
    if not nom:
        return "AUTRE"
    first = nom[0]
    if first.isalpha():
        return first.upper()
    return "AUTRE"


def resolve_parquet_path(base: str, nom: str) -> str:
    """Resolve partitioned (arbre-local) or single-file parquet path."""
    base = base.rstrip("/")
    if base.endswith(".parquet"):
        return base
    letter = partition_letter(nom)
    return f"{base}/lettre={letter}/data.parquet"


def _escape_sql_literal(value: str) -> str:
    return value.replace("'", "''")


def _build_where_clause(
    nom: str,
    prenom: str | None,
    birth_year_from: int | None,
    birth_year_to: int | None,
    commune: str | None,
    departement: str | None,
    *,
    include_opposition: bool = True,
) -> str:
    conditions = [f"nom = '{_escape_sql_literal(nom)}'"]

    if prenom:
        token = _escape_sql_literal(normalize_name(prenom))
        conditions.append(f"UPPER(prenoms) LIKE '%{token}%'")

    if birth_year_from is not None:
        conditions.append(f"date_naissance >= '{birth_year_from}0101'")
    if birth_year_to is not None:
        conditions.append(f"date_naissance <= '{birth_year_to}1231'")

    if commune:
        token = _escape_sql_literal(commune.strip())
        conditions.append(f"LOWER(commune_naissance) LIKE '%{token.lower()}%'")

    if departement:
        dept = re.sub(r"[^0-9AB]", "", departement.upper())[:3]
        if dept:
            conditions.append(f"substr(code_insee_naissance, 1, {len(dept)}) = '{dept}'")

    if include_opposition:
        conditions.append("(opposition IS NULL OR opposition = false)")

    return " AND ".join(conditions)


def _query_deaths_sync(
    parquet_path: str,
    nom: str,
    prenom: str | None,
    birth_year_from: int | None,
    birth_year_to: int | None,
    commune: str | None,
    departement: str | None,
    max_results: int,
) -> tuple[list[dict[str, Any]], list[str]]:
    import duckdb

    log: list[str] = []
    con = duckdb.connect()
    try:
        if parquet_path.startswith(("http://", "https://")):
            con.execute("INSTALL httpfs")
            con.execute("LOAD httpfs")

        escaped_path = parquet_path.replace("'", "''")
        select_sql = f"""
            SELECT nom, prenoms, sexe, date_naissance, code_insee_naissance,
                   commune_naissance, pays_naissance, date_deces,
                   code_insee_deces, numero_acte_deces
            FROM read_parquet('{escaped_path}')
        """

        last_error: Exception | None = None
        for include_opposition in (True, False):
            where = _build_where_clause(
                nom,
                prenom,
                birth_year_from,
                birth_year_to,
                commune,
                departement,
                include_opposition=include_opposition,
            )
            sql = f"{select_sql} WHERE {where} ORDER BY date_naissance ASC LIMIT {max_results}"
            try:
                rows = con.execute(sql).fetchall()
                columns = [
                    "nom", "prenoms", "sexe", "date_naissance", "code_insee_naissance",
                    "commune_naissance", "pays_naissance", "date_deces",
                    "code_insee_deces", "numero_acte_deces",
                ]
                results = [dict(zip(columns, row)) for row in rows]
                log.append(f"[DeathSearch] {len(results)} enregistrement(s) trouvé(s)")
                return results, log
            except Exception as exc:
                last_error = exc
                if not include_opposition:
                    break

        log.append(f"[DeathSearch] ERROR: {type(last_error).__name__ if last_error else 'Unknown'}")
        return [], log
    finally:
        con.close()


def _record_label(row: dict[str, Any]) -> str:
    prenoms = (row.get("prenoms") or "").replace(",", " ").strip()
    nom = row.get("nom") or ""
    birth = format_date_yyyymmdd(row.get("date_naissance"))
    death = format_date_yyyymmdd(row.get("date_deces"))
    parts = [p for p in [prenoms, nom] if p]
    label = " ".join(parts) if parts else nom or "Inconnu"
    if birth or death:
        extras = []
        if birth:
            extras.append(f"né {birth}")
        if death:
            extras.append(f"déc. {death}")
        label = f"{label} ({', '.join(extras)})"
    return label


class DeathSearchPlugin(TransformPlugin):
    async def run(self, context: PluginContext) -> dict:
        raw_label = context.entity.label.strip()
        nom, prenom = parse_person_label(raw_label)

        config_prenom = context.config.get("prenom") or context.config.get("first_name")
        if config_prenom:
            prenom = str(config_prenom).strip()

        if context.config.get("nom") or context.config.get("last_name"):
            nom = normalize_name(str(context.config.get("nom") or context.config.get("last_name")))

        if not nom:
            return {
                "nodes": [],
                "edges": [],
                "observations": [],
                "log": ["[DeathSearch] Nom de famille requis (ex. « Jean DUPONT » ou « DUPONT »)."],
            }

        birth_year_from = _optional_int(context.config.get("birth_year_from"))
        birth_year_to = _optional_int(context.config.get("birth_year_to"))
        commune = context.config.get("commune")
        departement = context.config.get("departement") or context.config.get("department")
        max_results = min(
            _optional_int(context.config.get("max_results")) or MAX_RESULTS_DEFAULT,
            MAX_RESULTS_HARD,
        )

        base_path = (
            context.config.get("data_path")
            or os.getenv("DEATH_RECORDS_PATH")
            or os.getenv("DEATH_RECORDS_BASE_URL")
        )

        if not base_path:
            return {
                "nodes": [],
                "edges": [],
                "observations": [],
                "log": [
                    "[DeathSearch] Données non configurées.",
                    "  Téléchargez « Agrégation des fichiers des personnes décédées » (Parquet) sur data.gouv.fr",
                    "  Puis configurez DEATH_RECORDS_PATH (fichier local ou dossier parts/)",
                    "  ou DEATH_RECORDS_BASE_URL (URL CDN partitionnée, voir arbre-local).",
                    f"  Source : {DATA_ATTRIBUTION}",
                ],
            }

        parquet_path = resolve_parquet_path(base_path, nom)
        context.log(f"[DeathSearch] Interrogation partition {partition_letter(nom)}…")

        rows, query_log = await asyncio.to_thread(
            _query_deaths_sync,
            parquet_path,
            nom,
            prenom,
            birth_year_from,
            birth_year_to,
            str(commune) if commune else None,
            str(departement) if departement else None,
            max_results,
        )

        nodes: list[dict] = []
        edges: list[dict] = []
        observations: list[dict] = []
        log = [
            f"[DeathSearch] Recherche : {nom}" + (f" / {prenom}" if prenom else ""),
            f"[DeathSearch] Filtres : naissance {birth_year_from or '—'}–{birth_year_to or '—'}, "
            f"commune={commune or '—'}, dept={departement or '—'}",
            *query_log,
            f"[DeathSearch] {DATA_ATTRIBUTION}",
        ]

        seed_label = raw_label
        seen_labels: set[str] = set()

        for idx, row in enumerate(rows):
            label = _record_label(row)
            if label in seen_labels:
                continue
            seen_labels.add(label)

            birth_place = row.get("commune_naissance") or row.get("pays_naissance") or ""
            props = {
                "source": DATA_SOURCE,
                "nom": row.get("nom") or "",
                "prenoms": row.get("prenoms") or "",
                "sexe": row.get("sexe") or "",
                "date_naissance": format_date_yyyymmdd(row.get("date_naissance")) or "",
                "date_deces": format_date_yyyymmdd(row.get("date_deces")) or "",
                "commune_naissance": row.get("commune_naissance") or "",
                "pays_naissance": row.get("pays_naissance") or "",
                "code_insee_naissance": row.get("code_insee_naissance") or "",
                "code_insee_deces": row.get("code_insee_deces") or "",
                "numero_acte_deces": row.get("numero_acte_deces") or "",
                "status": "UNVERIFIED",
                "attribution": DATA_ATTRIBUTION,
            }

            nodes.append({
                "type": "PERSON",
                "label": label,
                "properties": props,
            })
            edges.append({
                "source": seed_label,
                "target": label,
                "type": "LINKED_TO",
            })

            observations.append(build_observation(
                DATA_SOURCE,
                {
                    "field": "death_record",
                    "nom": props["nom"],
                    "prenoms": props["prenoms"],
                    "date_naissance": props["date_naissance"],
                    "commune_naissance": props["commune_naissance"],
                    "date_deces": props["date_deces"],
                    "numero_acte_deces": props["numero_acte_deces"],
                },
                collection_method="OFFICIAL_API",
                url="https://www.data.gouv.fr/fr/datasets/fichier-des-personnes-decedees/",
                confidence=0.6,
                status="UNVERIFIED",
            ))

            if birth_place and birth_place not in seen_labels:
                loc_label = birth_place
                if loc_label not in {n["label"] for n in nodes}:
                    nodes.append({
                        "type": "LOCATION",
                        "label": loc_label,
                        "properties": {
                            "source": DATA_SOURCE,
                            "code_insee": row.get("code_insee_naissance") or "",
                            "kind": "birth_commune",
                        },
                    })
                edges.append({
                    "source": label,
                    "target": loc_label,
                    "type": "LINKED_TO",
                })

            context.report_progress(f"Match {idx + 1}/{len(rows)}", idx + 1, len(rows))

        if not rows:
            log.append("[DeathSearch] Aucun résultat — affinez prénom, commune ou plage d'années.")

        return {"nodes": nodes, "edges": edges, "observations": observations, "log": log}


def _optional_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
