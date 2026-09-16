import React, { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, LayoutGrid } from 'lucide-react'
import { TransformHubModal } from '../components/modals/TransformHubModal'
import { useTranslation } from 'react-i18next'
import { MainLayout } from '../components/layout/MainLayout'
import { useInvestigationStore } from '../stores/investigationStore'
import { useGraphStore } from '../graph/graphStore'
import '../styles/maltego-workspace.css'

export const CarnetGraphPage: React.FC = () => {
  const { dossierId } = useParams<{ dossierId: string }>()
  const { t } = useTranslation()
  const { currentDossier, fetchDossier } = useInvestigationStore()
  const { fetchGraph, setWorkspace, nodes, edges } = useGraphStore()
  const [hubOpen, setHubOpen] = useState(false)

  useEffect(() => {
    if (!dossierId) return
    fetchDossier(dossierId)
  }, [dossierId, fetchDossier])

  useEffect(() => {
    if (!dossierId) return
    const workspace = currentDossier?.workspace_id ?? dossierId
    setWorkspace(workspace)
    fetchGraph(workspace)
  }, [dossierId, currentDossier?.workspace_id, fetchGraph, setWorkspace])

  return (
    <div className="investigation-workspace">
      <header className="maltego-investigation-bar">
        <div className="maltego-investigation-bar-left">
          <Link to={`/dossier/${dossierId}`} className="maltego-back">
            <ArrowLeft size={12} />
            {t('carnetView.backToCarnets')}
          </Link>
          <div className="maltego-investigation-meta">
            <span className="maltego-investigation-label">{t('graph.investigationLabel')}</span>
            <span className="maltego-investigation-name">
              {currentDossier?.name ?? t('dossier.title')}
            </span>
          </div>
        </div>
        <div className="maltego-investigation-bar-right">
          <button
            type="button"
            className="maltego-hub-btn"
            onClick={() => setHubOpen(true)}
          >
            <LayoutGrid size={14} />
            {t('transformHub.open')}
          </button>
          <span className="maltego-product-tag">
            {t('graph.linkAnalysis')} · {nodes.length} / {edges.length}
          </span>
        </div>
      </header>
      <TransformHubModal open={hubOpen} onClose={() => setHubOpen(false)} />
      <div className="investigation-workspace-body">
        <MainLayout />
      </div>
    </div>
  )
}
