import type { Carnet, Dossier } from '../types/domain'

export function isDossierEmpty(dossier: Dossier | null, carnets: Carnet[]): boolean {
  if (!dossier) return false
  const { persons = 0, accounts = 0, relations = 0 } = dossier.stats ?? {}
  const statsEmpty = persons === 0 && accounts === 0 && relations === 0
  const carnetsEmpty = carnets.length === 0 || carnets.every(c => c.entity_count === 0)
  return statsEmpty && carnetsEmpty
}
