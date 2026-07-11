"""Context Readiness Score before AI analysis."""
import os

from db.domain_client import domain_client
from models.domain import ContextReadinessOut

DEFAULT_THRESHOLD = int(os.getenv("AI_READINESS_THRESHOLD", "60"))


async def compute_readiness(entity_id: str) -> ContextReadinessOut:
    entity = await domain_client.get_entity(entity_id)
    observations = await domain_client.get_observations_for_entity(entity_id)

    async with await domain_client._connect() as db:
        async with db.execute(
            "SELECT COUNT(DISTINCT platform) FROM sources WHERE entity_id = ?",
            (entity_id,),
        ) as cur:
            platform_count = (await cur.fetchone())[0]
        async with db.execute(
            """SELECT COUNT(*) FROM relations
               WHERE source_entity_id = ? OR target_entity_id = ?""",
            (entity_id, entity_id),
        ) as cur:
            relation_count = (await cur.fetchone())[0]

    obs_count = len(observations)
    confirmed = sum(1 for o in observations if o.get("status") == "CONFIRMED")
    platforms = platform_count

    score = min(
        100,
        obs_count * 8 + platforms * 12 + relation_count * 5 + confirmed * 10 + int(entity.confidence * 20),
    )

    factors = {
        "observation_count": obs_count,
        "independent_sources": platforms,
        "relation_count": relation_count,
        "confirmed_observations": confirmed,
        "entity_confidence": entity.confidence,
    }

    sufficient = score >= DEFAULT_THRESHOLD
    message = (
        "Analyse assistée disponible."
        if sufficient
        else "Données insuffisantes pour une analyse fiable."
    )

    return ContextReadinessOut(
        score=score,
        sufficient=sufficient,
        threshold=DEFAULT_THRESHOLD,
        factors=factors,
        message=message,
    )
