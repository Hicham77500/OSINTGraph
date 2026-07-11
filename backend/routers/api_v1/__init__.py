"""
OSINTGraph — API v1 router
"""
from fastapi import APIRouter, HTTPException, Request

from db.domain_client import domain_client
from models.domain import (
    AIAnalysisRequest,
    CarnetCreate,
    DossierCreate,
    EntityCreate,
    RelationCreate,
)
from services.ai_analysis import analyze_entity
from services.context_readiness import compute_readiness
from services import entity_resolution

router = APIRouter()


def _actor(request: Request) -> str:
    return getattr(request.state, "actor", "local-analyst")


@router.get("/dossiers")
async def list_dossiers():
    return await domain_client.list_dossiers()


@router.post("/dossiers", status_code=201)
async def create_dossier(data: DossierCreate, request: Request):
    return await domain_client.create_dossier(data, actor=_actor(request))


@router.get("/dossiers/{dossier_id}")
async def get_dossier(dossier_id: str):
    try:
        return await domain_client.get_dossier(dossier_id)
    except ValueError:
        raise HTTPException(404, "Dossier not found")


@router.get("/dossiers/{dossier_id}/carnets")
async def list_carnets(dossier_id: str):
    return await domain_client.list_carnets(dossier_id)


@router.post("/dossiers/{dossier_id}/carnets", status_code=201)
async def create_carnet(dossier_id: str, data: CarnetCreate, request: Request):
    try:
        return await domain_client.create_carnet(dossier_id, data, actor=_actor(request))
    except Exception as e:
        raise HTTPException(400, str(e))


@router.get("/dossiers/{dossier_id}/entities")
async def list_entities(dossier_id: str, carnet_id: str | None = None, entity_type: str | None = None):
    return await domain_client.list_entities(dossier_id, carnet_id, entity_type)


@router.post("/dossiers/{dossier_id}/entities", status_code=201)
async def create_entity(dossier_id: str, data: EntityCreate, request: Request):
    return await domain_client.create_entity(dossier_id, data, actor=_actor(request))


@router.get("/entities/{entity_id}")
async def get_entity(entity_id: str):
    try:
        return await domain_client.get_entity(entity_id)
    except ValueError:
        raise HTTPException(404, "Entity not found")


@router.get("/entities/{entity_id}/observations")
async def get_observations(entity_id: str):
    return await domain_client.get_observations_for_entity(entity_id)


@router.get("/entities/{entity_id}/relations")
async def get_entity_relations(entity_id: str):
    entity = await domain_client.get_entity(entity_id)
    return await domain_client.list_relations(entity.dossier_id, entity_id)


@router.post("/dossiers/{dossier_id}/relations", status_code=201)
async def create_relation(dossier_id: str, data: RelationCreate, request: Request):
    return await domain_client.create_relation(dossier_id, data, actor=_actor(request))


@router.get("/entities/{entity_id}/readiness")
async def get_readiness(entity_id: str):
    return await compute_readiness(entity_id)


@router.post("/entities/{entity_id}/ai-analysis")
async def post_ai_analysis(entity_id: str, request: Request):
    result = await analyze_entity(entity_id)
    await domain_client.record_audit(
        _actor(request),
        "AI_ANALYSIS_REQUESTED",
        "entity",
        entity_id,
        None,
        {"claim": result.claim, "confidence": result.confidence},
    )
    return result


@router.get("/search")
async def global_search(q: str, limit: int = 20):
    return await domain_client.search(q, limit)


@router.get("/dossiers/{dossier_id}/merge-suggestions")
async def merge_suggestions(dossier_id: str):
    await entity_resolution.find_duplicates(dossier_id)
    return await entity_resolution.list_suggestions(dossier_id)


@router.post("/merge-suggestions/{suggestion_id}/reject")
async def reject_merge(suggestion_id: str, request: Request):
    await entity_resolution.reject_suggestion(suggestion_id, _actor(request))
    return {"ok": True}


@router.get("/audit")
async def list_audit(entity_id: str | None = None, limit: int = 50):
    return await domain_client.list_audit_events(entity_id, limit)
