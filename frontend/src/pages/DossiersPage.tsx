import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { FolderPlus, GitBranch, Share2, Trash2, Users } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { useInvestigationStore } from '../stores/investigationStore'
import './DossiersPage.css'

export const DossiersPage: React.FC = () => {
  const { t } = useTranslation()
  const { dossiers, fetchDossiers, createDossier, isLoading } = useInvestigationStore()
  const [showNew, setShowNew] = useState(false)
  const [name, setName] = useState('')

  useEffect(() => {
    fetchDossiers()
  }, [fetchDossiers])

  const handleCreate = async () => {
    if (!name.trim()) return
    await createDossier(name.trim())
    setName('')
    setShowNew(false)
  }

  return (
    <div className="workspace-page">
      <header className="workspace-header workspace-header-row">
        <div>
          <h1>OSINTGraph</h1>
          <p className="workspace-subtitle">{t('dossiers.subtitle')}</p>
        </div>
        <Link to="/trash" className="btn btn-ghost trash-link">
          <Trash2 size={16} />
          {t('dossiers.trash')}
        </Link>
      </header>

      {isLoading && <p className="workspace-loading">{t('dossiers.loading')}</p>}

      <div className="dossier-grid">
        {dossiers.map(d => (
          <Link key={d.id} to={`/dossier/${d.id}`} className="dossier-card glass-panel">
            <h2>{d.name}</h2>
            {d.description && <p className="dossier-desc">{d.description}</p>}
            <div className="dossier-stats">
              <span><Users size={14} /> {t('dossiers.statsPersons', { count: d.stats.persons ?? 0 })}</span>
              <span><Share2 size={14} /> {t('dossiers.statsAccounts', { count: d.stats.accounts ?? 0 })}</span>
              <span><GitBranch size={14} /> {t('dossiers.statsRelations', { count: d.stats.relations ?? 0 })}</span>
            </div>
          </Link>
        ))}

        <button className="dossier-card dossier-card-new glass-panel" onClick={() => setShowNew(true)}>
          <FolderPlus size={24} />
          <span>{t('dossiers.newDossier')}</span>
        </button>
      </div>

      {showNew && (
        <div className="modal-overlay" onClick={() => setShowNew(false)}>
          <div className="modal glass-panel" onClick={e => e.stopPropagation()}>
            <h3>{t('dossiers.newDossier')}</h3>
            <input
              value={name}
              onChange={e => setName(e.target.value)}
              placeholder={t('dossiers.namePlaceholder')}
              autoFocus
            />
            <div className="modal-actions">
              <button className="btn btn-ghost" onClick={() => setShowNew(false)}>
                {t('dossiers.cancel')}
              </button>
              <button className="btn btn-primary" onClick={handleCreate}>
                {t('dossiers.create')}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
