"""Entity resolution — merge suggestions only, never auto-merge."""
from difflib import SequenceMatcher

from db.domain_client import domain_client
from models.domain import MergeSuggestionOut, new_id


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


async def find_duplicates(dossier_id: str, threshold: float = 0.75) -> list[MergeSuggestionOut]:
    entities = await domain_client.list_entities(dossier_id)
    suggestions: list[MergeSuggestionOut] = []
    seen: set[tuple[str, str]] = set()

    for i, ea in enumerate(entities):
        for eb in entities[i + 1 :]:
            if ea.entity_type != eb.entity_type:
                continue
            pair = tuple(sorted([ea.id, eb.id]))
            if pair in seen:
                continue
            sim = _similarity(ea.label, eb.label)
            reasons: list[str] = []
            if sim >= 0.9:
                reasons.append("same username")
            elif sim >= 0.7:
                reasons.append("similar label")
            props_a = ea.properties or {}
            props_b = eb.properties or {}
            if props_a.get("url") and props_a.get("url") == props_b.get("url"):
                reasons.append("same external link")
                sim = max(sim, 0.85)
            if props_a.get("bio") and props_b.get("bio"):
                bio_sim = _similarity(str(props_a["bio"]), str(props_b["bio"]))
                if bio_sim > 0.8:
                    reasons.append("similar public bio")
                    sim = max(sim, bio_sim)

            if sim >= threshold and reasons:
                seen.add(pair)
                sid = new_id()
                async with await domain_client._session() as db:
                    await db.execute(
                        """INSERT OR IGNORE INTO merge_suggestions
                           (id, dossier_id, entity_a_id, entity_b_id, similarity, reasons, status)
                           VALUES (?, ?, ?, ?, ?, ?, 'PENDING')""",
                        (sid, dossier_id, ea.id, eb.id, sim, __import__("json").dumps(reasons)),
                    )
                    await db.commit()
                suggestions.append(
                    MergeSuggestionOut(
                        id=sid,
                        entity_a_id=ea.id,
                        entity_b_id=eb.id,
                        entity_a_label=ea.label,
                        entity_b_label=eb.label,
                        similarity=round(sim, 2),
                        reasons=reasons,
                        status="PENDING",
                    )
                )
    return suggestions


async def list_suggestions(dossier_id: str) -> list[MergeSuggestionOut]:
    import json

    async with domain_client._session() as db:
        db.row_factory = __import__("aiosqlite").Row
        async with db.execute(
            """SELECT ms.*, ea.label as label_a, eb.label as label_b
               FROM merge_suggestions ms
               JOIN entities ea ON ea.id = ms.entity_a_id
               JOIN entities eb ON eb.id = ms.entity_b_id
               WHERE ms.dossier_id = ? AND ms.status = 'PENDING'""",
            (dossier_id,),
        ) as cur:
            rows = await cur.fetchall()
    return [
        MergeSuggestionOut(
            id=r["id"],
            entity_a_id=r["entity_a_id"],
            entity_b_id=r["entity_b_id"],
            entity_a_label=r["label_a"],
            entity_b_label=r["label_b"],
            similarity=r["similarity"],
            reasons=json.loads(r["reasons"] or "[]"),
            status=r["status"],
        )
        for r in rows
    ]


async def reject_suggestion(suggestion_id: str, actor: str = "local-analyst") -> None:
    async with domain_client._session() as db:
        await db.execute(
            "UPDATE merge_suggestions SET status = 'REJECTED' WHERE id = ?", (suggestion_id,)
        )
        await db.commit()
    await domain_client.record_audit(
        actor, "MERGE_SUGGESTION_REJECTED", "merge_suggestion", suggestion_id, None, None
    )
