/**
 * Death records search — INSEE / data.gouv.fr (inspired by arbre-local).
 * Uses backend transform when available; optional client-side DuckDB-WASM
 * when VITE_DEATH_RECORDS_BASE_URL is configured.
 */
import { apiClient } from './api'

export interface DeathSearchParams {
  lastName: string
  firstName?: string
  birthYearFrom?: number
  birthYearTo?: number
  commune?: string
  departement?: string
}

export interface DeathRecord {
  label: string
  nom: string
  prenoms: string
  sexe: string
  date_naissance: string
  commune_naissance: string
  pays_naissance: string
  date_deces: string
  code_insee_naissance: string
  numero_acte_deces: string
}

export interface DeathSearchResult {
  records: DeathRecord[]
  log: string[]
  mode: 'backend' | 'client'
}

const CLIENT_BASE_URL = import.meta.env.VITE_DEATH_RECORDS_BASE_URL?.replace(/\/$/, '')

export function isClientDeathSearchAvailable(): boolean {
  return Boolean(CLIENT_BASE_URL)
}

function partitionLetter(nom: string): string {
  const first = nom.trim()[0]
  if (first && /[A-Za-z]/.test(first)) return first.toUpperCase()
  return 'AUTRE'
}

function formatDate(raw: string | null | undefined): string {
  if (!raw || raw.length !== 8 || !/^\d+$/.test(raw)) return raw ?? ''
  return `${raw.slice(6, 8)}/${raw.slice(4, 6)}/${raw.slice(0, 4)}`
}

function buildLabel(row: Record<string, string>): string {
  const prenoms = (row.prenoms ?? '').replace(/,/g, ' ').trim()
  const nom = row.nom ?? ''
  const birth = formatDate(row.date_naissance)
  const death = formatDate(row.date_deces)
  let label = [prenoms, nom].filter(Boolean).join(' ') || nom
  if (birth || death) {
    const parts: string[] = []
    if (birth) parts.push(`né ${birth}`)
    if (death) parts.push(`déc. ${death}`)
    label = `${label} (${parts.join(', ')})`
  }
  return label
}

function mapNodeToRecord(node: { label: string; properties?: Record<string, string> }): DeathRecord {
  const p = node.properties ?? {}
  return {
    label: node.label,
    nom: p.nom ?? '',
    prenoms: p.prenoms ?? '',
    sexe: p.sexe ?? '',
    date_naissance: p.date_naissance ?? '',
    commune_naissance: p.commune_naissance ?? '',
    pays_naissance: p.pays_naissance ?? '',
    date_deces: p.date_deces ?? '',
    code_insee_naissance: p.code_insee_naissance ?? '',
    numero_acte_deces: p.numero_acte_deces ?? '',
  }
}

export async function searchDeathRecords(params: DeathSearchParams): Promise<DeathSearchResult> {
  if (isClientDeathSearchAvailable()) {
    try {
      const records = await searchDeathRecordsClient(params)
      return {
        records,
        log: ['[DeathSearch] Recherche locale (navigateur) — aucun nom envoyé au serveur.'],
        mode: 'client',
      }
    } catch {
      // Fall back to backend if WASM init fails
    }
  }
  return searchDeathRecordsBackend(params)
}

async function searchDeathRecordsBackend(params: DeathSearchParams): Promise<DeathSearchResult> {
  const value = params.firstName
    ? `${params.firstName} ${params.lastName}`
    : params.lastName

  const res = await apiClient.post('/transforms/run', {
    transform: 'death_search',
    input_type: 'PERSON',
    value,
    options: {
      nom: params.lastName.toUpperCase(),
      prenom: params.firstName,
      birth_year_from: params.birthYearFrom || undefined,
      birth_year_to: params.birthYearTo || undefined,
      commune: params.commune || undefined,
      departement: params.departement || undefined,
    },
  })

  const data = res.data as {
    ok?: boolean
    nodes?: Array<{ type: string; label: string; properties?: Record<string, string> }>
    log?: string[]
    error?: string
  } | null

  if (!res.ok || !data?.ok) {
    return {
      records: [],
      log: data?.log ?? [data?.error ?? 'Erreur lors de la recherche'],
      mode: 'backend',
    }
  }

  const records = (data.nodes ?? [])
    .filter(n => n.type === 'PERSON')
    .map(mapNodeToRecord)

  return {
    records,
    log: data.log ?? [],
    mode: 'backend',
  }
}

/** Client-side search via DuckDB-WASM + remote Parquet (arbre-local architecture). */
export async function searchDeathRecordsClient(params: DeathSearchParams): Promise<DeathRecord[]> {
  if (!CLIENT_BASE_URL) {
    throw new Error('VITE_DEATH_RECORDS_BASE_URL not configured')
  }

  const duckdb = await import('@duckdb/duckdb-wasm')
  const bundles = duckdb.getJsDelivrBundles()
  const bundle = await duckdb.selectBundle(bundles)
  const worker = new Worker(bundle.mainWorker!)
  const logger = new duckdb.ConsoleLogger()
  const db = new duckdb.AsyncDuckDB(logger, worker)
  await db.instantiate(bundle.mainModule, bundle.pthreadWorker)
  const conn = await db.connect()

  const nom = params.lastName.trim().toUpperCase()
  const letter = partitionLetter(nom)
  const parquetUrl = `${CLIENT_BASE_URL}/lettre=${letter}/data.parquet`

  const conditions = [`nom = '${nom.replace(/'/g, "''")}'`]
  if (params.firstName) {
    const prenom = params.firstName.toUpperCase().replace(/'/g, "''")
    conditions.push(`UPPER(prenoms) LIKE '%${prenom}%'`)
  }
  if (params.birthYearFrom) {
    conditions.push(`date_naissance >= '${params.birthYearFrom}0101'`)
  }
  if (params.birthYearTo) {
    conditions.push(`date_naissance <= '${params.birthYearTo}1231'`)
  }
  if (params.commune) {
    conditions.push(`LOWER(commune_naissance) LIKE '%${params.commune.toLowerCase().replace(/'/g, "''")}%'`)
  }
  if (params.departement) {
    const dept = params.departement.replace(/[^0-9AB]/gi, '').slice(0, 3)
    if (dept) conditions.push(`substr(code_insee_naissance, 1, ${dept.length}) = '${dept}'`)
  }

  const sql = `
    SELECT nom, prenoms, sexe, date_naissance, code_insee_naissance,
           commune_naissance, pays_naissance, date_deces, numero_acte_deces
    FROM read_parquet('${parquetUrl}')
    WHERE ${conditions.join(' AND ')}
    ORDER BY date_naissance ASC
    LIMIT 100
  `

  const result = await conn.query(sql)
  await conn.close()
  await db.terminate()

  return result.toArray().map((row: Record<string, unknown>) => {
    const r = Object.fromEntries(
      Object.entries(row).map(([k, v]) => [k, v == null ? '' : String(v)])
    ) as Record<string, string>
    return {
      label: buildLabel(r),
      nom: r.nom ?? '',
      prenoms: r.prenoms ?? '',
      sexe: r.sexe ?? '',
      date_naissance: formatDate(r.date_naissance),
      commune_naissance: r.commune_naissance ?? '',
      pays_naissance: r.pays_naissance ?? '',
      date_deces: formatDate(r.date_deces),
      code_insee_naissance: r.code_insee_naissance ?? '',
      numero_acte_deces: r.numero_acte_deces ?? '',
    }
  })
}
