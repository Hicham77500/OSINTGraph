export type ConfidenceStatus =
  | 'CONFIRMED'
  | 'LIKELY'
  | 'POSSIBLE'
  | 'UNVERIFIED'
  | 'CONTRADICTED'

export interface Dossier {
  id: string
  name: string
  description?: string
  workspace_id?: string
  created_at: string
  updated_at: string
  deleted_at?: string | null
  stats: { persons: number; accounts: number; relations: number }
}

export interface Carnet {
  id: string
  dossier_id: string
  name: string
  notebook_type: string
  entity_count: number
  created_at: string
}

export interface Entity {
  id: string
  dossier_id: string
  carnet_id?: string
  entity_type: string
  label: string
  properties: Record<string, unknown>
  confidence: number
  status: ConfidenceStatus
  created_at: string
  updated_at: string
}

export interface Observation {
  id: string
  content: Record<string, unknown>
  confidence: number
  status: string
  observed_at: string
  platform: string
  collection_method: string
  url?: string
  collected_at: string
}

export interface Relation {
  id: string
  dossier_id: string
  source_entity_id: string
  target_entity_id: string
  relation_type: string
  confidence: number
  status: string
  evidence_ids: string[]
  created_at: string
}

export interface ContextReadiness {
  score: number
  sufficient: boolean
  threshold: number
  factors: Record<string, number>
  message: string
}

export interface AIAnalysis {
  claim: string
  reasoning_summary: string
  evidence_ids: string[]
  confidence: number
  contradictions: string[]
  status: ConfidenceStatus
  matches?: Array<{ entity_id: string; label: string; relation_type: string; confidence: number }>
  gaps?: string[]
  next_steps?: string[]
}

export interface SearchResult {
  id: string
  label: string
  entity_type: string
  dossier_id: string
  dossier_name: string
  match_type: 'exact' | 'normalized' | 'potential'
}
