import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { FolderPlus, Users, Share2, GitBranch } from 'lucide-react'
import { useInvestigationStore } from '../stores/investigationStore'
import './DossiersPage.css'

export const DossiersPage: React.FC = () => {
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
      <header className="workspace-header">
        <h1>OSINTGraph</h1>
        <p className="workspace-subtitle">Mes dossiers</p>
      </header>

      {isLoading && <p className="workspace-loading">Chargement…</p>}

      <div className="dossier-grid">
        {dossiers.map(d => (
          <Link key={d.id} to={`/dossier/${d.id}`} className="dossier-card glass-panel">
            <h2>{d.name}</h2>
            {d.description && <p className="dossier-desc">{d.description}</p>}
            <div className="dossier-stats">
              <span><Users size={14} /> {d.stats.persons ?? 0} personnes</span>
              <span><Share2 size={14} /> {d.stats.accounts ?? 0} comptes</span>
              <span><GitBranch size={14} /> {d.stats.relations ?? 0} relations</span>
            </div>
          </Link>
        ))}

        <button className="dossier-card dossier-card-new glass-panel" onClick={() => setShowNew(true)}>
          <FolderPlus size={24} />
          <span>Nouveau dossier</span>
        </button>
      </div>

      {showNew && (
        <div className="modal-overlay" onClick={() => setShowNew(false)}>
          <div className="modal glass-panel" onClick={e => e.stopPropagation()}>
            <h3>Nouveau dossier</h3>
            <input
              value={name}
              onChange={e => setName(e.target.value)}
              placeholder="Nom de l'investigation"
              autoFocus
            />
            <div className="modal-actions">
              <button className="btn btn-ghost" onClick={() => setShowNew(false)}>Annuler</button>
              <button className="btn btn-primary" onClick={handleCreate}>Créer</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
