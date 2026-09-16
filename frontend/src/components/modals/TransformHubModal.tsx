import React, { useEffect, useMemo, useState } from 'react'
import { X, Search, KeyRound, CheckCircle2, CircleDashed, ExternalLink } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { apiClient } from '../../services/api'
import { ApiKeyHelp, type ApiKeyHelpItem } from '../common/ApiKeyHelp'
import './TransformHubModal.css'

type HubEntry = {
  id: string
  name: string
  provider: string
  description: string
  category: string
  plugin_id?: string | null
  env_keys?: string[]
  acquisition?: string
  status?: string
  installed?: boolean
  configured?: boolean
  tags?: string[]
  api_key_help?: ApiKeyHelpItem[]
}

type HubResponse = {
  entries: HubEntry[]
  stats: { total: number; installed: number; configured: number }
}

type FilterMode = 'all' | 'installed' | 'not_installed'

interface TransformHubModalProps {
  open: boolean
  onClose: () => void
}

export const TransformHubModal: React.FC<TransformHubModalProps> = ({ open, onClose }) => {
  const { t } = useTranslation()
  const [entries, setEntries] = useState<HubEntry[]>([])
  const [stats, setStats] = useState<HubResponse['stats'] | null>(null)
  const [query, setQuery] = useState('')
  const [filter, setFilter] = useState<FilterMode>('all')
  const [loading, setLoading] = useState(false)
  const [apiKeyItems, setApiKeyItems] = useState<ApiKeyHelpItem[]>([])

  useEffect(() => {
    if (!open) return
    setLoading(true)
    Promise.all([
      apiClient.get('/transforms/hub'),
      apiClient.get('/transforms/api-keys'),
    ]).then(([hubRes, keysRes]) => {
      if (hubRes.ok && hubRes.data) {
        const data = hubRes.data as HubResponse
        setEntries(data.entries ?? [])
        setStats(data.stats ?? null)
      }
      if (keysRes.ok && keysRes.data) {
        const items = (keysRes.data as { items?: ApiKeyHelpItem[] }).items ?? []
        setApiKeyItems(items)
      }
    }).finally(() => setLoading(false))
  }, [open])

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    return entries.filter(e => {
      if (filter === 'installed' && !e.installed) return false
      if (filter === 'not_installed' && e.installed) return false
      if (!q) return true
      const hay = `${e.name} ${e.provider} ${e.description} ${e.category} ${(e.tags ?? []).join(' ')}`.toLowerCase()
      return hay.includes(q)
    })
  }, [entries, filter, query])

  if (!open) return null

  return (
    <div className="transform-hub-overlay" role="dialog" aria-modal="true" aria-labelledby="transform-hub-title">
      <div className="transform-hub-panel">
        <header className="transform-hub-header">
          <div>
            <h2 id="transform-hub-title">{t('transformHub.title')}</h2>
            <p className="transform-hub-subtitle">{t('transformHub.subtitle')}</p>
          </div>
          <button type="button" className="transform-hub-close" onClick={onClose} aria-label={t('transformHub.close')}>
            <X size={18} />
          </button>
        </header>

        <div className="transform-hub-toolbar">
          <div className="transform-hub-search">
            <Search size={14} />
            <input
              type="search"
              placeholder={t('transformHub.filterPlaceholder')}
              value={query}
              onChange={ev => setQuery(ev.target.value)}
            />
          </div>
          <div className="transform-hub-filters">
            {(['all', 'installed', 'not_installed'] as const).map(mode => (
              <button
                key={mode}
                type="button"
                className={filter === mode ? 'active' : ''}
                onClick={() => setFilter(mode)}
              >
                {t(`transformHub.filter.${mode}`)}
              </button>
            ))}
          </div>
          {stats && (
            <span className="transform-hub-stats">
              {t('transformHub.stats', {
                shown: filtered.length,
                total: stats.total,
                installed: stats.installed,
              })}
            </span>
          )}
          {apiKeyItems.length > 0 && (
            <div className="transform-hub-api-banner">
              <ApiKeyHelp items={apiKeyItems} variant="inline" />
            </div>
          )}
        </div>

        {apiKeyItems.length > 0 && (
          <div className="transform-hub-quick-links" aria-label={t('transformHub.apiKey.quickLinks')}>
            {apiKeyItems.map(item => item.signup_url && (
              <a
                key={item.env_key}
                href={item.signup_url}
                target="_blank"
                rel="noopener noreferrer"
                className="transform-hub-quick-link"
                title={item.env_key}
              >
                <ExternalLink size={11} aria-hidden />
                {item.provider ?? item.env_key}
              </a>
            ))}
          </div>
        )}

        {loading ? (
          <div className="transform-hub-loading">{t('transformHub.loading')}</div>
        ) : (
          <div className="transform-hub-grid">
            {filtered.map(entry => (
              <article key={entry.id} className={`transform-hub-card ${entry.installed ? 'installed' : ''}`}>
                <div className="transform-hub-card-top">
                  <h3>{entry.name}</h3>
                  {entry.status === 'planned' && !entry.installed && (
                    <span className="hub-badge planned">{t('transformHub.planned')}</span>
                  )}
                  {entry.installed && (
                    <span className="hub-badge installed">{t('transformHub.installed')}</span>
                  )}
                </div>
                <p className="hub-provider">{t('transformHub.byProvider', { provider: entry.provider })}</p>
                <p className="hub-desc">{entry.description}</p>
                <div className="hub-card-footer">
                  <span className="hub-category">{entry.category}</span>
                  <div className="hub-card-footer-actions">
                    {entry.env_keys && entry.env_keys.length > 0 && (
                      <ApiKeyHelp
                        items={entry.api_key_help ?? entry.env_keys.map(k => ({ env_key: k }))}
                        variant="compact"
                      />
                    )}
                    {entry.installed && entry.env_keys && entry.env_keys.length > 0 && (
                      <span className={`hub-key ${entry.configured ? 'ok' : 'missing'}`} title={entry.env_keys.join(', ')}>
                        {entry.configured ? <CheckCircle2 size={12} /> : <KeyRound size={12} />}
                        {entry.configured ? t('transformHub.keyOk') : t('transformHub.keyMissing')}
                      </span>
                    )}
                  </div>
                  {!entry.installed && (
                    <span className="hub-key muted">
                      <CircleDashed size={12} />
                      {t('transformHub.notBundled')}
                    </span>
                  )}
                </div>
              </article>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
