// ============================================================
// API Client — OsintGraph
// Points at FastAPI backend on http://localhost:8000
// Falls back to window.osint.api (Electron IPC) if available
// ============================================================

const BASE_URL = 'http://localhost:8000'

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

export const apiClient = {
  get: (path: string) => request('GET', path),
  post: (path: string, body?: unknown) => request('POST', path, body),
  put: (path: string, body?: unknown) => request('PUT', path, body),
  patch: (path: string, body?: unknown) => request('PATCH', path, body),
  delete: (path: string) => request('DELETE', path),
}
