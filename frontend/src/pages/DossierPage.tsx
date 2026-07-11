import React, { useEffect } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, ChevronRight } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { useInvestigationStore } from '../stores/investigationStore'
import { carnetDescriptionKey, carnetIcon, graphIcon } from '../utils/carnetMeta'
import { isDossierEmpty } from '../utils/dossierUtils'
import './DossiersPage.css'

export const DossierPage: React.FC = () => {
  const { dossierId } = useParams<{ dossierId: string }>()
  const { t } = useTranslation()
  const { currentDossier, carnets, fetchDossier, fetchCarnets } = useInvestigationStore()

  useEffect(() => {
    if (dossierId) {
      fetchDossier(dossierId)
      fetchCarnets(dossierId)
    }
  }, [dossierId, fetchDossier, fetchCarnets])

  if (!dossierId) return null

  const empty = isDossierEmpty(currentDossier, carnets)

  return (
    <div className="workspace-page">
      <Link to="/" className="back-link">
        <ArrowLeft size={14} /> {t('dossier.backToDossiers')}
      </Link>

      <header className="workspace-header">
        <h1>{currentDossier?.name ?? t('dossier.title')}</h1>
        <p className="workspace-subtitle">{t('dossier.hubSubtitle')}</p>
      </header>

      {empty && (
        <section className="onboarding-banner glass-panel" aria-label={t('dossier.welcomeTitle')}>
          <h2>{t('dossier.welcomeTitle')}</h2>
          <p className="onboarding-lead">{t('dossier.welcomeLead')}</p>
          <ol className="onboarding-steps">
            <li>{t('dossier.workflowStep1')}</li>
            <li>{t('dossier.workflowStep2')}</li>
            <li>{t('dossier.workflowStep3')}</li>
          </ol>
        </section>
      )}

      <Link
        to={`/dossier/${dossierId}/graph`}
        className="graph-hero-card glass-panel"
      >
        <div className="graph-hero-icon">{graphIcon(28)}</div>
        <div className="graph-hero-content">
          <h2>{t('dossier.fullGraph')}</h2>
          <p>{t('dossier.graphHeroDesc')}</p>
        </div>
        <span className="graph-hero-cta btn btn-primary">
          {t('dossier.openGraph')}
          <ChevronRight size={16} />
        </span>
      </Link>

      <section className="carnet-section">
        <h2 className="carnet-section-title">{t('dossier.investigationAxes')}</h2>
        <div className="carnet-grid">
          {carnets.map(c => (
            <Link
              key={c.id}
              to={`/dossier/${dossierId}/carnet/${c.id}`}
              className="carnet-card glass-panel"
            >
              <div className="carnet-card-icon">{carnetIcon(c.notebook_type)}</div>
              <h3>{c.name}</h3>
              <p className="carnet-desc">
                {t(carnetDescriptionKey(c.notebook_type), { defaultValue: c.notebook_type })}
              </p>
              <p className="carnet-count">{t('dossier.entityCount', { count: c.entity_count })}</p>
            </Link>
          ))}
        </div>
      </section>
    </div>
  )
}
