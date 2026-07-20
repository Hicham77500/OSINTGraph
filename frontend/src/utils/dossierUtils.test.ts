import { describe, expect, it } from 'vitest'
import { isDossierEmpty } from './dossierUtils'
import type { Carnet, Dossier } from '../types/domain'

const baseDossier: Dossier = {
  id: 'd1',
  name: 'Test',
  created_at: '2026-01-01',
  updated_at: '2026-01-01',
  stats: { persons: 0, accounts: 0, relations: 0 },
}

const baseCarnet: Carnet = {
  id: 'c1',
  dossier_id: 'd1',
  name: 'Personnes',
  notebook_type: 'personnes',
  entity_count: 0,
  created_at: '2026-01-01',
}

describe('isDossierEmpty', () => {
  it('returns true when stats and carnets are all zero', () => {
    expect(isDossierEmpty(baseDossier, [baseCarnet])).toBe(true)
  })

  it('returns false when dossier has person stats', () => {
    expect(isDossierEmpty(
      { ...baseDossier, stats: { persons: 1, accounts: 0, relations: 0 } },
      [baseCarnet],
    )).toBe(false)
  })

  it('returns false when a carnet has entities', () => {
    expect(isDossierEmpty(baseDossier, [{ ...baseCarnet, entity_count: 2 }])).toBe(false)
  })

  it('returns false when dossier is null', () => {
    expect(isDossierEmpty(null, [])).toBe(false)
  })
})
