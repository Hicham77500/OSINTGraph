import { create } from 'zustand'
import { apiClient } from '../services/api'
import type { Carnet, Dossier, Entity } from '../types/domain'

interface InvestigationState {
  dossiers: Dossier[]
  currentDossier: Dossier | null
  carnets: Carnet[]
  entities: Entity[]
  isLoading: boolean
  error: string | null

  fetchDossiers: () => Promise<void>
  fetchDossier: (id: string) => Promise<void>
  fetchCarnets: (dossierId: string) => Promise<void>
  fetchEntities: (dossierId: string, carnetId?: string) => Promise<void>
  createDossier: (name: string, description?: string) => Promise<Dossier | null>
  createCarnet: (dossierId: string, name: string) => Promise<void>
  createEntity: (
    dossierId: string,
    data: {
      entity_type: string
      label: string
      carnet_id?: string
      properties?: Record<string, unknown>
    },
  ) => Promise<Entity | null>
  updateEntity: (
    entityId: string,
    data: {
      label?: string
      properties?: Record<string, unknown>
    },
    dossierId?: string,
    carnetId?: string,
  ) => Promise<Entity | null>
  deleteEntity: (entityId: string, dossierId?: string, carnetId?: string) => Promise<boolean>
  fetchTrashDossiers: () => Promise<Dossier[]>
  softDeleteDossier: (dossierId: string) => Promise<boolean>
  restoreDossier: (dossierId: string) => Promise<boolean>
  permanentDeleteDossier: (dossierId: string) => Promise<boolean>
  setCurrentDossier: (dossier: Dossier | null) => void
}

export const useInvestigationStore = create<InvestigationState>((set, get) => ({
  dossiers: [],
  currentDossier: null,
  carnets: [],
  entities: [],
  isLoading: false,
  error: null,

  fetchDossiers: async () => {
    set({ isLoading: true, error: null })
    const res = await apiClient.get('/api/v1/dossiers')
    if (res.ok && res.data) {
      set({ dossiers: res.data as Dossier[], isLoading: false })
    } else {
      set({ isLoading: false, error: res.error || 'Failed to load dossiers' })
    }
  },

  fetchDossier: async (id: string) => {
    set({ isLoading: true })
    const res = await apiClient.get(`/api/v1/dossiers/${id}`)
    if (res.ok && res.data) {
      set({ currentDossier: res.data as Dossier, isLoading: false })
    } else {
      set({ isLoading: false, error: 'Dossier not found' })
    }
  },

  fetchCarnets: async (dossierId: string) => {
    const res = await apiClient.get(`/api/v1/dossiers/${dossierId}/carnets`)
    if (res.ok && res.data) {
      set({ carnets: res.data as Carnet[] })
    }
  },

  fetchEntities: async (dossierId: string, carnetId?: string) => {
    const qs = carnetId ? `?carnet_id=${carnetId}` : ''
    const res = await apiClient.get(`/api/v1/dossiers/${dossierId}/entities${qs}`)
    if (res.ok && res.data) {
      set({ entities: res.data as Entity[] })
    }
  },

  createDossier: async (name: string, description?: string) => {
    const res = await apiClient.post('/api/v1/dossiers', { name, description })
    if (res.ok && res.data) {
      await get().fetchDossiers()
      return res.data as Dossier
    }
    return null
  },

  createCarnet: async (dossierId: string, name: string) => {
    await apiClient.post(`/api/v1/dossiers/${dossierId}/carnets`, { name, notebook_type: 'custom' })
    await get().fetchCarnets(dossierId)
  },

  createEntity: async (dossierId, data) => {
    const res = await apiClient.post(`/api/v1/dossiers/${dossierId}/entities`, data)
    if (res.ok && res.data) {
      if (data.carnet_id) {
        await get().fetchEntities(dossierId, data.carnet_id)
      }
      await get().fetchCarnets(dossierId)
      return res.data as Entity
    }
    return null
  },

  updateEntity: async (entityId, data, dossierId, carnetId) => {
    const res = await apiClient.patch(`/api/v1/entities/${entityId}`, data)
    if (res.ok && res.data) {
      if (dossierId && carnetId) {
        await get().fetchEntities(dossierId, carnetId)
      }
      return res.data as Entity
    }
    return null
  },

  deleteEntity: async (entityId, dossierId, carnetId) => {
    const res = await apiClient.delete(`/api/v1/entities/${entityId}`)
    if (res.ok) {
      if (dossierId && carnetId) {
        await get().fetchEntities(dossierId, carnetId)
      }
      return true
    }
    return false
  },

  fetchTrashDossiers: async () => {
    const res = await apiClient.get('/api/v1/dossiers/trash')
    if (res.ok && res.data) {
      return res.data as Dossier[]
    }
    return []
  },

  softDeleteDossier: async (dossierId) => {
    const res = await apiClient.delete(`/api/v1/dossiers/${dossierId}`)
    if (res.ok) {
      await get().fetchDossiers()
      if (get().currentDossier?.id === dossierId) {
        set({ currentDossier: null })
      }
      return true
    }
    return false
  },

  restoreDossier: async (dossierId) => {
    const res = await apiClient.post(`/api/v1/dossiers/${dossierId}/restore`)
    return res.ok
  },

  permanentDeleteDossier: async (dossierId) => {
    const res = await apiClient.delete(`/api/v1/dossiers/${dossierId}/permanent`)
    return res.ok
  },

  setCurrentDossier: (dossier) => set({ currentDossier: dossier }),
}))
