import { describe, expect, it } from 'vitest'
import {
  getActRequestEligibility,
  parseBirthYear,
  departmentFromInsee,
} from './civilRegistryRequest'
import type { DeathRecord } from '../services/deathSearch'

const baseRecord: DeathRecord = {
  label: 'Jean DUPONT',
  nom: 'DUPONT',
  prenoms: 'JEAN',
  sexe: 'M',
  date_naissance: '15/03/1950',
  commune_naissance: 'PARIS',
  pays_naissance: '',
  date_deces: '10/01/2020',
  code_insee_naissance: '75056',
  numero_acte_deces: '123',
}

describe('parseBirthYear', () => {
  it('parses DD/MM/YYYY', () => {
    expect(parseBirthYear('15/03/1950')).toBe(1950)
  })
})

describe('departmentFromInsee', () => {
  it('extracts metro dept', () => {
    expect(departmentFromInsee('75056')).toBe('75')
  })
})

describe('getActRequestEligibility', () => {
  it('allows death act without filiation', () => {
    const r = getActRequestEligibility(baseRecord, 'death', { filiationJustified: false })
    expect(r.allowed).toBe(true)
    expect(r.requiresFiliationProof).toBe(false)
  })

  it('blocks recent birth act without filiation proof', () => {
    const recent: DeathRecord = {
      ...baseRecord,
      date_naissance: '15/03/2000',
    }
    const r = getActRequestEligibility(recent, 'birth', {
      filiationJustified: false,
      referenceYear: 2026,
    })
    expect(r.allowed).toBe(false)
    expect(r.requiresFiliationProof).toBe(true)
  })

  it('allows recent birth act when filiation justified', () => {
    const recent: DeathRecord = {
      ...baseRecord,
      date_naissance: '15/03/2000',
    }
    const r = getActRequestEligibility(recent, 'birth', {
      filiationJustified: true,
      referenceYear: 2026,
    })
    expect(r.allowed).toBe(true)
  })

  it('allows old birth act via archives without filiation checkbox', () => {
    const old: DeathRecord = {
      ...baseRecord,
      date_naissance: '15/03/1940',
    }
    const r = getActRequestEligibility(old, 'birth', {
      filiationJustified: false,
      referenceYear: 2026,
    })
    expect(r.allowed).toBe(true)
    expect(r.requiresFiliationProof).toBe(false)
  })
})
