import { describe, expect, it } from 'vitest'
import en from './locales/en'
import fr from './locales/fr'

type TranslationTree = Record<string, string | TranslationTree>

function collectLeafPaths(obj: TranslationTree, prefix = ''): string[] {
  const paths: string[] = []
  for (const [key, value] of Object.entries(obj)) {
    const path = prefix ? `${prefix}.${key}` : key
    if (value !== null && typeof value === 'object') {
      paths.push(...collectLeafPaths(value as TranslationTree, path))
    } else {
      paths.push(path)
    }
  }
  return paths.sort()
}

function getByPath(obj: TranslationTree, path: string): string | undefined {
  let current: string | TranslationTree | undefined = obj
  for (const key of path.split('.')) {
    if (!current || typeof current !== 'object') return undefined
    current = current[key]
  }
  return typeof current === 'string' ? current : undefined
}

const ALLOW_IDENTICAL = new Set([
  'entityPanel.sectionTypes',
  'inspector.propSource',
  'dossier.title',
  'carnetView.types.notes',
  'transforms.catalog.hibp_lookup.display_name',
  'personView.backToDossier',
  'personView.ai.readinessTitle',
  'commandSearch.matchExact',
  'dossiers.statsRelations',
  'personView.tabs.relations',
])

const MUST_DIFFER = [
  'toolbar.save',
  'dossiers.subtitle',
  'trash.title',
  'canvas.emptyTitle',
  'commandSearch.placeholder',
  'personView.tabs.overview',
  'graph.focusNode',
  'personView.ai.runAnalysis',
]

describe('i18n locale parity', () => {
  const enPaths = collectLeafPaths(en as TranslationTree)
  const frPaths = collectLeafPaths(fr as TranslationTree)

  it('en and fr expose the same translation keys', () => {
    expect(frPaths).toEqual(enPaths)
  })

  it('has no empty translation values', () => {
    for (const path of enPaths) {
      expect(getByPath(en as TranslationTree, path), `${path} (en)`).not.toBe('')
      expect(getByPath(fr as TranslationTree, path), `${path} (fr)`).not.toBe('')
    }
  })

  it('translates critical UI keys (not copy-pasted across locales)', () => {
    for (const path of MUST_DIFFER) {
      const enValue = getByPath(en as TranslationTree, path)
      const frValue = getByPath(fr as TranslationTree, path)
      expect(enValue, path).toBeTruthy()
      expect(frValue, path).toBeTruthy()
      expect(enValue).not.toBe(frValue)
    }
  })

  it('flags likely untranslated fr strings copied from en', () => {
    const identicalOutsideAllowlist = enPaths.filter(path => {
      if (ALLOW_IDENTICAL.has(path)) return false
      const enValue = getByPath(en as TranslationTree, path)
      const frValue = getByPath(fr as TranslationTree, path)
      return enValue === frValue
    })

    expect(identicalOutsideAllowlist).toEqual([])
  })
})
