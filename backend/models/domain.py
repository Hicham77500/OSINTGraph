"""
OSINTGraph — Domain Pydantic models
"""
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def new_id() -> str:
    return str(uuid4())


class ConfidenceStatus(str, Enum):
    CONFIRMED = "CONFIRMED"
    LIKELY = "LIKELY"
    POSSIBLE = "POSSIBLE"
    UNVERIFIED = "UNVERIFIED"
    CONTRADICTED = "CONTRADICTED"


class CollectionMethod(str, Enum):
    MANUAL = "MANUAL"
    PUBLIC_SEARCH = "PUBLIC_SEARCH"
    OFFICIAL_API = "OFFICIAL_API"
    IMPORT = "IMPORT"
    TRANSFORM = "TRANSFORM"


class EntityType(str, Enum):
    PERSON = "PERSON"
    ORGANIZATION = "ORGANIZATION"
    ALIAS = "ALIAS"
    USERNAME = "USERNAME"
    SOCIAL_ACCOUNT = "SOCIAL_ACCOUNT"
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    DOMAIN = "DOMAIN"
    WEBSITE = "WEBSITE"
    LOCATION = "LOCATION"
    EVENT = "EVENT"
    DOCUMENT = "DOCUMENT"
    MEDIA = "MEDIA"
    CUSTOM = "CUSTOM"


class RelationType(str, Enum):
    USES = "USES"
    KNOWS = "KNOWS"
    FOLLOWS = "FOLLOWS"
    WORKS_AT = "WORKS_AT"
    MEMBER_OF = "MEMBER_OF"
    OWNS = "OWNS"
    CREATED = "CREATED"
    MENTIONED_BY = "MENTIONED_BY"
    LOCATED_AT = "LOCATED_AT"
    RELATED_TO = "RELATED_TO"
    RESOLVES_TO = "RESOLVES_TO"
    LINKED_TO = "LINKED_TO"


class NotebookType(str, Enum):
    PERSONNES = "personnes"
    RESEAUX_SOCIAUX = "reseaux_sociaux"
    ENTREPRISES = "entreprises"
    PSEUDONYMES = "pseudonymes"
    TELEPHONES = "telephones"
    EMAILS = "emails"
    DOMAINES = "domaines"
    EVENEMENTS = "evenements"
    CHRONOLOGIE = "chronologie"
    NOTES = "notes"
    CUSTOM = "custom"


class DossierCreate(BaseModel):
    name: str
    description: str | None = None


class DossierOut(BaseModel):
    id: str
    name: str
    description: str | None = None
    workspace_id: str | None = None
    created_at: str
    updated_at: str
    stats: dict[str, int] = Field(default_factory=dict)


class CarnetCreate(BaseModel):
    name: str
    notebook_type: NotebookType = NotebookType.CUSTOM


class CarnetOut(BaseModel):
    id: str
    dossier_id: str
    name: str
    notebook_type: str
    entity_count: int = 0
    created_at: str


class EntityCreate(BaseModel):
    entity_type: EntityType
    label: str
    carnet_id: str | None = None
    properties: dict[str, Any] = Field(default_factory=dict)
    confidence: float = 0.5
    status: ConfidenceStatus = ConfidenceStatus.UNVERIFIED


class EntityOut(BaseModel):
    id: str
    dossier_id: str
    carnet_id: str | None = None
    entity_type: str
    label: str
    properties: dict[str, Any] = Field(default_factory=dict)
    confidence: float
    status: str
    created_at: str
    updated_at: str


class SourceOut(BaseModel):
    id: str
    entity_id: str
    platform: str
    url: str | None = None
    collection_method: str
    collected_at: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ObservationOut(BaseModel):
    id: str
    source_id: str
    entity_id: str
    content: dict[str, Any]
    observed_at: str
    confidence: float
    status: str


class EvidenceOut(BaseModel):
    id: str
    observation_id: str | None = None
    relation_id: str | None = None
    hypothesis_id: str | None = None
    summary: str
    confidence: float
    status: str


class RelationCreate(BaseModel):
    source_entity_id: str
    target_entity_id: str
    relation_type: RelationType
    confidence: float = 0.5
    status: ConfidenceStatus = ConfidenceStatus.UNVERIFIED
    evidence_ids: list[str] = Field(default_factory=list)


class RelationOut(BaseModel):
    id: str
    dossier_id: str
    source_entity_id: str
    target_entity_id: str
    relation_type: str
    confidence: float
    status: str
    evidence_ids: list[str] = Field(default_factory=list)
    created_at: str


class HypothesisOut(BaseModel):
    id: str
    dossier_id: str
    entity_id: str | None = None
    claim: str
    reasoning_summary: str
    evidence_ids: list[str] = Field(default_factory=list)
    confidence: float
    contradictions: list[str] = Field(default_factory=list)
    status: str
    source: str
    analyst_action: str | None = None
    created_at: str


class MergeSuggestionOut(BaseModel):
    id: str
    entity_a_id: str
    entity_b_id: str
    entity_a_label: str
    entity_b_label: str
    similarity: float
    reasons: list[str]
    status: str


class ContextReadinessOut(BaseModel):
    score: int
    sufficient: bool
    threshold: int
    factors: dict[str, Any]
    message: str


class AIAnalysisRequest(BaseModel):
    entity_id: str


class AIAnalysisOut(BaseModel):
    claim: str
    reasoning_summary: str
    evidence_ids: list[str]
    confidence: float
    contradictions: list[str]
    status: ConfidenceStatus
    hypotheses: list[HypothesisOut] = Field(default_factory=list)
    matches: list[dict[str, Any]] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)


class SearchResult(BaseModel):
    id: str
    label: str
    entity_type: str
    dossier_id: str
    dossier_name: str
    match_type: str  # exact, normalized, potential
    context: str | None = None


class AuditEventOut(BaseModel):
    id: str
    actor: str
    action: str
    entity_type: str
    entity_id: str
    previous_state: dict[str, Any] | None = None
    new_state: dict[str, Any] | None = None
    timestamp: str
