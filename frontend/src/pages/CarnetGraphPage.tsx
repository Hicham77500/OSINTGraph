import React, { useEffect } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { MainLayout } from '../components/layout/MainLayout'
import { useInvestigationStore } from '../stores/investigationStore'
import { useGraphStore } from '../graph/graphStore'

export const CarnetGraphPage: React.FC = () => {
  const { dossierId } = useParams<{ dossierId: string }>()
  const { t } = useTranslation()
  const { currentDossier, fetchDossier } = useInvestigationStore()
  const { fetchGraph, setWorkspace } = useGraphStore()

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
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      <Link to={`/dossier/${dossierId}`} className="back-link" style={{ padding: '0.5rem 1rem' }}>
        <ArrowLeft size={14} /> {t('carnetView.backToCarnets')}
      </Link>
      <div style={{ flex: 1, minHeight: 0 }}>
        <MainLayout />
      </div>
    </div>
  )
}
