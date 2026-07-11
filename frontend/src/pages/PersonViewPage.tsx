import React, { useEffect, useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import {
  ArrowLeft, User, Share2, GitBranch, Clock, FileSearch, Sparkles,
} from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { apiClient } from '../services/api'
import type { AIAnalysis, ContextReadiness, Entity, Observation, Relation } from '../types/domain'
import './PersonViewPage.css'

type Tab = 'overview' | 'identities' | 'social' | 'relations' | 'timeline' | 'evidence' | 'ai'

export const PersonViewPage: React.FC = () => {
  const { dossierId, entityId } = useParams<{ dossierId: string; entityId: string }>()
  const { t } = useTranslation()
  const [entity, setEntity] = useState<Entity | null>(null)
  const [observations, setObservations] = useState<Observation[]>([])
  const [relations, setRelations] = useState<Relation[]>([])
  const [readiness, setReadiness] = useState<ContextReadiness | null>(null)
  const [analysis, setAnalysis] = useState<AIAnalysis | null>(null)
  const [tab, setTab] = useState<Tab>('overview')

  useEffect(() => {
    if (!entityId) return
    apiClient.get(`/api/v1/entities/${entityId}`).then(r => {
      if (r.ok) setEntity(r.data as Entity)
    })
    apiClient.get(`/api/v1/entities/${entityId}/observations`).then(r => {
      if (r.ok) setObservations(r.data as Observation[])
    })
    apiClient.get(`/api/v1/entities/${entityId}/relations`).then(r => {
      if (r.ok) setRelations(r.data as Relation[])
    })
    apiClient.get(`/api/v1/entities/${entityId}/readiness`).then(r => {
      if (r.ok) setReadiness(r.data as ContextReadiness)
    })
  }, [entityId])

  const runAnalysis = async () => {
    if (!entityId) return
    const res = await apiClient.post(`/api/v1/entities/${entityId}/ai-analysis`)
    if (res.ok) setAnalysis(res.data as AIAnalysis)
  }

  const tabs = useMemo(() => ([
    { id: 'overview' as const, label: t('personView.tabs.overview'), icon: <User size={14} /> },
    { id: 'identities' as const, label: t('personView.tabs.identities'), icon: <User size={14} /> },
    { id: 'social' as const, label: t('personView.tabs.social'), icon: <Share2 size={14} /> },
    { id: 'relations' as const, label: t('personView.tabs.relations'), icon: <GitBranch size={14} /> },
    { id: 'timeline' as const, label: t('personView.tabs.timeline'), icon: <Clock size={14} /> },
    { id: 'evidence' as const, label: t('personView.tabs.evidence'), icon: <FileSearch size={14} /> },
    { id: 'ai' as const, label: t('personView.tabs.ai'), icon: <Sparkles size={14} /> },
  ]), [t])

  if (!entity) {
    return <div className="person-view loading">{t('personView.loading')}</div>
  }

  const socialObs = observations.filter(o =>
    ['instagram', 'tiktok', 'linkedin', 'github', 'x', 'facebook'].includes(o.platform)
  )

  return (
    <div className="person-view">
      <Link to={`/dossier/${dossierId}`} className="back-link">
        <ArrowLeft size={14} /> {t('personView.backToDossier')}
      </Link>

      <header className="person-header glass-panel">
        <div className="person-avatar"><User size={32} /></div>
        <div className="person-meta">
          <h1>{entity.label}</h1>
          <p className="person-type">{entity.entity_type}</p>
          <div className="person-badges">
            <span className={`badge badge-${entity.status.toLowerCase()}`}>{entity.status}</span>
            <span className="badge">
              {t('personView.confidence', { percent: Math.round(entity.confidence * 100) })}
            </span>
            <span className="badge">{t('personView.sources', { count: observations.length })}</span>
          </div>
        </div>
      </header>

      <nav className="person-tabs">
        {tabs.map(item => (
          <button
            key={item.id}
            className={`person-tab ${tab === item.id ? 'active' : ''}`}
            onClick={() => setTab(item.id)}
          >
            {item.icon} {item.label}
          </button>
        ))}
      </nav>

      <div className="person-content glass-panel">
        {tab === 'overview' && (
          <div>
            <h3>{t('personView.overview.title')}</h3>
            <p>{t('personView.overview.identity', { label: entity.label, type: entity.entity_type })}</p>
            <p>{t('personView.overview.properties', { props: JSON.stringify(entity.properties) })}</p>
            <p>{t('personView.overview.keyObservations', { count: observations.length })}</p>
          </div>
        )}

        {tab === 'social' && (
          <div className="social-grid">
            {socialObs.length === 0 && <p>{t('personView.social.empty')}</p>}
            {socialObs.map(o => (
              <div key={o.id} className="social-card">
                <h4>{o.platform}</h4>
                <p>{String(o.content.value ?? JSON.stringify(o.content))}</p>
                <div className="social-meta">
                  <span className={`badge badge-${o.status.toLowerCase()}`}>{o.status}</span>
                  <span>{o.collection_method}</span>
                  <span>{new Date(o.collected_at).toLocaleDateString()}</span>
                </div>
              </div>
            ))}
          </div>
        )}

        {tab === 'relations' && (
          <ul className="relation-list">
            {relations.map(r => (
              <li key={r.id}>
                {t('personView.relations.item', {
                  type: r.relation_type,
                  percent: Math.round(r.confidence * 100),
                })}
                <span className={`badge badge-${r.status.toLowerCase()}`}>{r.status}</span>
                <span className="evidence-count">
                  {t('personView.relations.evidenceCount', { count: r.evidence_ids.length })}
                </span>
              </li>
            ))}
          </ul>
        )}

        {tab === 'timeline' && (
          <ul className="timeline">
            {observations.map(o => (
              <li key={o.id}>
                <time>{new Date(o.observed_at).toLocaleDateString()}</time>
                <span>
                  {t('personView.timeline.item', {
                    platform: o.platform,
                    value: String(o.content.value ?? o.content.field),
                  })}
                </span>
              </li>
            ))}
          </ul>
        )}

        {tab === 'evidence' && (
          <div>
            {observations.map(o => (
              <div key={o.id} className="evidence-item">
                <span>{o.platform}</span>
                <span>{o.status}</span>
                <span>{Math.round(o.confidence * 100)}%</span>
                <code>{JSON.stringify(o.content)}</code>
              </div>
            ))}
          </div>
        )}

        {tab === 'ai' && (
          <div>
            {readiness && (
              <div className={`readiness ${readiness.sufficient ? 'ready' : 'not-ready'}`}>
                <h4>{t('personView.ai.readinessTitle', { score: readiness.score })}</h4>
                <p>{readiness.message}</p>
              </div>
            )}
            {readiness?.sufficient ? (
              <>
                {!analysis && (
                  <button className="btn btn-primary" onClick={runAnalysis}>
                    {t('personView.ai.runAnalysis')}
                  </button>
                )}
                {analysis && (
                  <div className="ai-result">
                    <p className="ai-claim">{analysis.claim}</p>
                    <p>{analysis.reasoning_summary}</p>
                    <span className={`badge badge-${analysis.status.toLowerCase()}`}>{analysis.status}</span>
                    <div className="ai-actions">
                      <button className="btn btn-primary">{t('personView.ai.confirm')}</button>
                      <button className="btn btn-ghost">{t('personView.ai.reject')}</button>
                      <button className="btn btn-ghost">{t('personView.ai.markForReview')}</button>
                    </div>
                  </div>
                )}
              </>
            ) : (
              <p className="text-muted">{t('personView.ai.insufficientData')}</p>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
