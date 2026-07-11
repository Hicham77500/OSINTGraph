"""Rule-based AI analysis scaffold — replace with external provider when configured."""
import os

from db.domain_client import domain_client
from models.domain import AIAnalysisOut, ConfidenceStatus, HypothesisOut
from services.context_readiness import compute_readiness


async def analyze_entity(entity_id: str) -> AIAnalysisOut:
    readiness = await compute_readiness(entity_id)
    if not readiness.sufficient:
        return AIAnalysisOut(
            claim="Analyse non disponible — contexte insuffisant",
            reasoning_summary=readiness.message,
            evidence_ids=[],
            confidence=0.0,
            contradictions=[],
            status=ConfidenceStatus.UNVERIFIED,
            gaps=["Ajouter des sources indépendantes", "Documenter des observations"],
            next_steps=["Collecter identifiants sur sources publiques", "Lier comptes sociaux"],
        )

    entity = await domain_client.get_entity(entity_id)
    observations = await domain_client.get_observations_for_entity(entity_id)
    evidence_ids = [o["id"] for o in observations[:5]]

    provider = os.getenv("AI_PROVIDER", "rule-based")
    if provider != "rule-based" and os.getenv("AI_API_KEY"):
        # Placeholder for future OpenAI/Anthropic/Ollama integration
        pass

    relations = await domain_client.list_relations(entity.dossier_id, entity_id)
    matches = []
    for rel in relations[:3]:
        try:
            other_id = rel.target_entity_id if rel.source_entity_id == entity_id else rel.source_entity_id
            other = await domain_client.get_entity(other_id)
            matches.append(
                {
                    "entity_id": other.id,
                    "label": other.label,
                    "relation_type": rel.relation_type,
                    "confidence": rel.confidence,
                }
            )
        except ValueError:
            continue

    hypothesis = HypothesisOut(
        id="pending",
        dossier_id=entity.dossier_id,
        entity_id=entity_id,
        claim=f"Profil '{entity.label}' — {len(observations)} observations sur {readiness.factors.get('independent_sources', 0)} sources",
        reasoning_summary="Synthèse basée sur observations et relations documentées (copilote, pas source de vérité)",
        evidence_ids=evidence_ids,
        confidence=min(0.85, readiness.score / 100),
        contradictions=[],
        status=ConfidenceStatus.POSSIBLE.value,
        source="AI",
        analyst_action=None,
        created_at=entity.updated_at,
    )

    return AIAnalysisOut(
        claim=hypothesis.claim,
        reasoning_summary=hypothesis.reasoning_summary,
        evidence_ids=evidence_ids,
        confidence=hypothesis.confidence,
        contradictions=[],
        status=ConfidenceStatus.POSSIBLE,
        hypotheses=[hypothesis],
        matches=matches,
        gaps=["Vérifier concordance cross-plateforme"] if readiness.score < 80 else [],
        next_steps=["Confirmer ou rejeter les hypothèses suggérées"],
    )
