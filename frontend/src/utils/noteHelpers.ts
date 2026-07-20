import type { Entity, Observation } from '../types/domain'

export const SEED_MARKER_LABEL = '__osintgraph_demo_seed_v1__'

export type NoteItem = {
  entityId: string
  title: string
  text: string
  createdAt: string
  updatedAt: string
  observedAt?: string
}

export function isHiddenNoteEntity(entity: Entity): boolean {
  return entity.label === SEED_MARKER_LABEL
}

export function noteContentFromEntity(entity: Entity): string {
  if (typeof entity.properties.content === 'string') return entity.properties.content
  if (typeof entity.properties.notes === 'string') return entity.properties.notes
  return ''
}

export function noteTitleFromEntity(entity: Entity): string {
  if (typeof entity.properties.title === 'string') return entity.properties.title
  return entity.label
}

export function findNoteObservedAt(observations: Observation[]): string | undefined {
  for (const o of observations) {
    if (o.platform === 'manual' && o.content.field === 'notes') {
      return o.observed_at
    }
  }
  return undefined
}

export function collectNoteItems(
  entities: Entity[],
  observationsByEntity: Map<string, Observation[]>,
): NoteItem[] {
  const items: NoteItem[] = []
  for (const entity of entities) {
    if (isHiddenNoteEntity(entity)) continue
    const content = noteContentFromEntity(entity)
    if (!content.trim()) continue
    const obs = observationsByEntity.get(entity.id) ?? []
    items.push({
      entityId: entity.id,
      title: noteTitleFromEntity(entity),
      text: content,
      createdAt: entity.created_at,
      updatedAt: entity.updated_at,
      observedAt: findNoteObservedAt(obs),
    })
  }
  return items
}

export function formatNoteDate(iso: string, locale: string): string {
  return new Date(iso).toLocaleString(locale, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}
