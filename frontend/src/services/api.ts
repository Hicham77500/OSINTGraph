// ============================================================
// API Client — OsintGraph
// Dev: Vite proxy or http://localhost:8000 via VITE_API_BASE
// Docker/nginx: empty VITE_API_BASE → same-origin relative paths
// Electron: window.osint.api IPC bridge
// ============================================================

const BASE_URL = import.meta.env.VITE_API_BASE ?? ''

export interface ApiResponse {
  ok: boolean
  status: number
  data?: unknown
  error?: string
}

async function request(method: string, path: string, body?: unknown): Promise<ApiResponse> {
  // Electron IPC bridge
  const w = window as any
  if (w.osint?.api) {
    return w.osint.api.call(method, path, body)
  }

  // Direct fetch (browser / Vite dev)
  try {
    const res = await fetch(`${BASE_URL}${path}`, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: body !== undefined ? JSON.stringify(body) : undefined,
    })
    const data = res.ok ? await res.json().catch(() => null) : null
    return { ok: res.ok, status: res.status, data }
  } catch (err: any) {
    return { ok: false, status: 0, error: err.message }
  }
}

async function postForm(path: string, body: FormData): Promise<ApiResponse> {
  const w = window as any
  if (w.osint?.api?.postForm) {
    return w.osint.api.postForm(path, body)
  }
  try {
    const res = await fetch(`${BASE_URL}${path}`, { method: 'POST', body })
    const data = res.ok ? await res.json().catch(() => null) : null
    if (!res.ok) {
      const err = (data as { detail?: string })?.detail
      return { ok: false, status: res.status, data, error: err ?? res.statusText }
    }
    return { ok: res.ok, status: res.status, data }
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err)
    return { ok: false, status: 0, error: message }
  }
}

export const apiClient = {
  get: (path: string) => request('GET', path),
  post: (path: string, body?: unknown) => request('POST', path, body),
  postForm,
  put: (path: string, body?: unknown) => request('PUT', path, body),
  patch: (path: string, body?: unknown) => request('PATCH', path, body),
  delete: (path: string) => request('DELETE', path),
}
