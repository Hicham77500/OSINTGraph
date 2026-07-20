import { describe, expect, it } from 'vitest'
import {
  SEED_MARKER_LABEL,
  collectNoteItems,
  isHiddenNoteEntity,
  noteContentFromEntity,
  noteTitleFromEntity,
} from './noteHelpers'
import type { Entity, Observation } from '../types/domain'

const baseEntity: Entity = {
  id: 'e1',
  dossier_id: 'd1',
  carnet_id: 'c1',
  entity_type: 'CUSTOM',
  label: 'My note',
  properties: { title: 'Title', content: 'Body text' },
  confidence: 0.5,
  status: 'UNVERIFIED',
  created_at: '2026-01-01T10:00:00',
  updated_at: '2026-01-02T10:00:00',
}

describe('noteHelpers', () => {
  it('hides seed marker entity', () => {
    expect(isHiddenNoteEntity({ ...baseEntity, label: SEED_MARKER_LABEL })).toBe(true)
    expect(isHiddenNoteEntity(baseEntity)).toBe(false)
  })

  it('extracts title and content from entity properties', () => {
    expect(noteTitleFromEntity(baseEntity)).toBe('Title')
    expect(noteContentFromEntity(baseEntity)).toBe('Body text')
    expect(noteContentFromEntity({ ...baseEntity, properties: { notes: 'Legacy' } })).toBe('Legacy')
  })

  it('collects note items and skips empty or marker entities', () => {
    const obs: Observation = {
      id: 'o1',
      content: { field: 'notes', value: 'Body text' },
      confidence: 0.5,
      status: 'UNVERIFIED',
      observed_at: '2026-01-03T12:00:00',
      platform: 'manual',
      collection_method: 'MANUAL',
      collected_at: '2026-01-03T12:00:00',
    }
    const items = collectNoteItems(
      [baseEntity, { ...baseEntity, id: 'e2', label: SEED_MARKER_LABEL, properties: { content: 'x' } }],
      new Map([[baseEntity.id, [obs]]]),
    )
    expect(items).toHaveLength(1)
    expect(items[0].entityId).toBe('e1')
    expect(items[0].observedAt).toBe('2026-01-03T12:00:00')
  })
})
