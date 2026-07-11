import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowLeft, RotateCcw, Trash2 } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { useInvestigationStore } from '../stores/investigationStore'
import type { Dossier } from '../types/domain'
import './DossiersPage.css'

export const TrashPage: React.FC = () => {
  const { t } = useTranslation()
  const { fetchTrashDossiers, restoreDossier, permanentDeleteDossier } = useInvestigationStore()
  const [trash, setTrash] = useState<Dossier[]>([])
  const [loading, setLoading] = useState(true)
  const [busyId, setBusyId] = useState<string | null>(null)

  const loadTrash = async () => {
    setLoading(true)
    const items = await fetchTrashDossiers()
    setTrash(items)
    setLoading(false)
  }

  useEffect(() => {
    loadTrash()
  }, [fetchTrashDossiers])

  const handleRestore = async (id: string) => {
    setBusyId(id)
    const ok = await restoreDossier(id)
    if (ok) await loadTrash()
    setBusyId(null)
  }

  const handlePermanentDelete = async (dossier: Dossier) => {
    if (!window.confirm(t('trash.permanentDeleteConfirm', { name: dossier.name }))) return
    setBusyId(dossier.id)
    const ok = await permanentDeleteDossier(dossier.id)
    if (ok) await loadTrash()
    setBusyId(null)
  }

  return (
    <div className="workspace-page">
      <Link to="/" className="back-link">
        <ArrowLeft size={14} /> {t('trash.backToDossiers')}
      </Link>

      <header className="workspace-header">
        <h1>{t('trash.title')}</h1>
        <p className="workspace-subtitle">{t('trash.subtitle')}</p>
      </header>

      {loading && <p className="workspace-loading">{t('trash.loading')}</p>}

      {!loading && trash.length === 0 && (
        <div className="trash-empty glass-panel">
          <p>{t('trash.empty')}</p>
        </div>
      )}

      <div className="dossier-grid">
        {trash.map(d => (
          <div key={d.id} className="dossier-card dossier-card-trash glass-panel">
            <h2>{d.name}</h2>
            {d.description && <p className="dossier-desc">{d.description}</p>}
            {d.deleted_at && (
              <p className="trash-deleted-at">
                {t('trash.deletedAt', { date: new Date(d.deleted_at).toLocaleString() })}
              </p>
            )}
            <div className="trash-actions">
              <button
                className="btn btn-primary"
                disabled={busyId === d.id}
                onClick={() => handleRestore(d.id)}
              >
                <RotateCcw size={14} />
                {t('trash.restore')}
              </button>
              <button
                className="btn btn-ghost btn-danger"
                disabled={busyId === d.id}
                onClick={() => handlePermanentDelete(d)}
              >
                <Trash2 size={14} />
                {t('trash.deletePermanent')}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
