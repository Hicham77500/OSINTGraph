/**
 * Civil registry act request — legal eligibility and mailto helpers.
 * OSINTGraph never sends mail automatically; opens the analyst's mail client.
 */
import type { DeathRecord } from '../services/deathSearch'

export type ActKind = 'death' | 'birth'

export interface ActRequestEligibility {
  allowed: boolean
  reasonKey: string
  requiresFiliationProof: boolean
  recipientHintKey: string
}

const ARCHIVES_75_YEARS = 75
const FRANCEARCHIVES_ANNUAIRE = 'https://francearchives.gouv.fr/fr/annuaire'

export function parseBirthYear(dateStr: string | undefined): number | null {
  if (!dateStr) return null
  const slash = dateStr.match(/^(\d{2})\/(\d{2})\/(\d{4})$/)
  if (slash) return Number(slash[3])
  const compact = dateStr.match(/^(\d{4})(\d{2})(\d{2})$/)
  if (compact) return Number(compact[1])
  const yearOnly = dateStr.match(/^(\d{4})$/)
  if (yearOnly) return Number(yearOnly[1])
  return null
}

export function departmentFromInsee(code: string | undefined): string {
  if (!code || code.length < 2) return ''
  if (code.startsWith('97') || code.startsWith('98')) return code.slice(0, 3)
  return code.slice(0, 2)
}

export function getActRequestEligibility(
  record: DeathRecord,
  kind: ActKind,
  options: { filiationJustified: boolean; referenceYear?: number },
): ActRequestEligibility {
  const refYear = options.referenceYear ?? new Date().getFullYear()
  const birthYear = parseBirthYear(record.date_naissance)
  const dept = departmentFromInsee(record.code_insee_naissance)

  if (kind === 'death') {
    if (!record.date_deces) {
      return {
        allowed: false,
        reasonKey: 'deathSearch.act.noDeathDate',
        requiresFiliationProof: false,
        recipientHintKey: 'deathSearch.act.recipientMairie',
      }
    }
    return {
      allowed: true,
      reasonKey: 'deathSearch.act.deathEligible',
      requiresFiliationProof: false,
      recipientHintKey: 'deathSearch.act.recipientMairieDeath',
    }
  }

  // Birth act
  if (!record.commune_naissance && !record.pays_naissance) {
    return {
      allowed: false,
      reasonKey: 'deathSearch.act.noBirthPlace',
      requiresFiliationProof: false,
      recipientHintKey: 'deathSearch.act.recipientArchives',
    }
  }

  if (birthYear === null) {
    return {
      allowed: false,
      reasonKey: 'deathSearch.act.noBirthDate',
      requiresFiliationProof: true,
      recipientHintKey: 'deathSearch.act.recipientUnknown',
    }
  }

  const age = refYear - birthYear
  const isRecent = age < ARCHIVES_75_YEARS

  if (isRecent && !options.filiationJustified) {
    return {
      allowed: false,
      reasonKey: 'deathSearch.act.birthNeedsFiliation',
      requiresFiliationProof: true,
      recipientHintKey: 'deathSearch.act.recipientMairieBirth',
    }
  }

  return {
    allowed: true,
    reasonKey: isRecent
      ? 'deathSearch.act.birthEligibleMairie'
      : 'deathSearch.act.birthEligibleArchives',
    requiresFiliationProof: isRecent,
    recipientHintKey: isRecent
      ? 'deathSearch.act.recipientMairieBirth'
      : 'deathSearch.act.recipientArchivesDept',
  }
}

export function buildActRequestMailto(
  record: DeathRecord,
  kind: ActKind,
  labels: {
    subjectDeath: string
    subjectBirth: string
    bodyDeath: string
    bodyBirth: string
    filiationNote: string
  },
  options: { filiationJustified: boolean },
): string {
  const prenoms = record.prenoms.replace(/,/g, ' ')
  const dept = departmentFromInsee(record.code_insee_naissance)
  const archivesUrl = dept
    ? `${FRANCEARCHIVES_ANNUAIRE}?dept=${encodeURIComponent(dept)}`
    : FRANCEARCHIVES_ANNUAIRE

  const filiationBlock =
    options.filiationJustified && kind === 'birth'
      ? `\n\n${labels.filiationNote}`
      : ''

  let subject: string
  let body: string

  if (kind === 'death') {
    subject = labels.subjectDeath
    body = labels.bodyDeath
      .replace('{{nom}}', record.nom)
      .replace('{{prenoms}}', prenoms)
      .replace('{{date_naissance}}', record.date_naissance || '—')
      .replace('{{commune_naissance}}', record.commune_naissance || record.pays_naissance || '—')
      .replace('{{date_deces}}', record.date_deces || '—')
      .replace('{{numero_acte}}', record.numero_acte_deces || '—')
  } else {
    subject = labels.subjectBirth
    body = labels.bodyBirth
      .replace('{{nom}}', record.nom)
      .replace('{{prenoms}}', prenoms)
      .replace('{{date_naissance}}', record.date_naissance || '—')
      .replace('{{commune_naissance}}', record.commune_naissance || record.pays_naissance || '—')
      .replace('{{departement}}', dept || '—')
      .replace('{{archives_url}}', archivesUrl)
      + filiationBlock
  }

  const params = new URLSearchParams()
  params.set('subject', subject)
  params.set('body', body)
  return `mailto:?${params.toString()}`
}

export function getArchivesAnnuaireUrl(record: DeathRecord): string {
  const dept = departmentFromInsee(record.code_insee_naissance)
  if (!dept) return FRANCEARCHIVES_ANNUAIRE
  return `${FRANCEARCHIVES_ANNUAIRE}?dept=${encodeURIComponent(dept)}`
}
