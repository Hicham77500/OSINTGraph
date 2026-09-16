import { apiClient } from './api'

export type VisualSearchAssistant = {
  id: string
  name: string
  url: string
  method: string
  hint?: string
}

export type VisualSearchUploadResult = {
  ok: boolean
  asset_id: string
  filename: string
  content_type: string
  sha256: string
  public_url: string
  linked_person?: string | null
  linked_place?: string | null
  assistants: VisualSearchAssistant[]
  disclaimer?: string
}

export async function uploadInvestigationImage(
  file: File,
  linkedPerson?: string,
  linkedPlace?: string,
): Promise<{ ok: boolean; data?: VisualSearchUploadResult; error?: string }> {
  const form = new FormData()
  form.append('file', file)
  const params = new URLSearchParams()
  if (linkedPerson) params.set('linked_person', linkedPerson)
  if (linkedPlace) params.set('linked_place', linkedPlace)
  const qs = params.toString()
  const path = `/api/v1/investigation/visual-search/upload${qs ? `?${qs}` : ''}`

  const res = await apiClient.postForm(path, form)
  if (!res.ok) {
    return { ok: false, error: res.error ?? 'Upload failed' }
  }
  return { ok: true, data: res.data as VisualSearchUploadResult }
}

export function assetDownloadUrl(assetId: string): string {
  const base = import.meta.env.VITE_API_BASE ?? ''
  return `${base}/api/v1/investigation/assets/${assetId}`
}
