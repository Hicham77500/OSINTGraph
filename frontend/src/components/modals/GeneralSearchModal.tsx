import React, { useMemo, useState } from 'react'
import { X, ExternalLink, Search, Globe, Users, MessageSquare, Phone, Car } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { apiClient } from '../../services/api'
import { createEdge, createNode, type EdgeData, type NodeData } from '../../graph/nodeTypes'
import './GeneralSearchModal.css'

type Mode = 'web' | 'person' | 'social' | 'forum' | 'phone' | 'plate'

type Assistant = {
  id: string
  name: string
  url: string
  category?: string
  keyword?: string
}

type ResultCardDto = {
  title?: string
  url: string
  snippet?: string
  source_engine?: string
}

const FORUM_PRESETS = ['reddit', 'forum', 'leak', 'breach', 'credential', 'pirate', 'warez', 'dump'] as const

interface GeneralSearchModalProps {
  open: boolean
  onClose: () => void
  initialQuery?: string
  initialMode?: Mode
  onAttachToGraph?: (nodes: NodeData[], edges: EdgeData[]) => void
}

export const GeneralSearchModal: React.FC<GeneralSearchModalProps> = ({
  open,
  onClose,
  initialQuery = '',
  initialMode = 'web',
  onAttachToGraph,
}) => {
  const { t } = useTranslation()
  const [query, setQuery] = useState(initialQuery)
  const [mode, setMode] = useState<Mode>(initialMode)
  const [keywords, setKeywords] = useState<string[]>(['reddit', 'forum', 'leak', 'pirate', 'breach', 'credential'])
  const [assistants, setAssistants] = useState<Assistant[]>([])
  const [loading, setLoading] = useState(false)
  const [disclaimer, setDisclaimer] = useState<string | null>(null)

  const modeTabs = useMemo(() => ([
    { id: 'web' as const, icon: Globe, label: t('generalSearch.tabs.web') },
    { id: 'person' as const, icon: Search, label: t('generalSearch.tabs.person') },
    { id: 'social' as const, icon: Users, label: t('generalSearch.tabs.social') },
    { id: 'forum' as const, icon: MessageSquare, label: t('generalSearch.tabs.forum') },
    { id: 'phone' as const, icon: Phone, label: t('generalSearch.tabs.phone') },
    { id: 'plate' as const, icon: Car, label: t('generalSearch.tabs.plate') },
  ]), [t])

  const runSearch = async () => {
    if (!query.trim()) return
    setLoading(true)
    const params = new URLSearchParams({ q: query.trim(), mode, fetch: 'true' })
    if (mode === 'forum') params.set('keywords', keywords.join(','))
    const res = await apiClient.get(`/api/v1/investigation/general-search?${params}`)
    setLoading(false)
    if (res.ok && res.data) {
      const data = res.data as { assistants: Assistant[]; result_cards?: ResultCardDto[]; disclaimer?: string }
      const cards = data.result_cards ?? []
      setAssistants(cards.length > 0 ? cards.map(c => ({
        id: c.url,
        name: c.title || c.url,
        url: c.url,
      })) : (data.assistants ?? []))
      setDisclaimer(data.disclaimer ?? null)
    } else {
      setAssistants([])
    }
  }

  const toggleKeyword = (kw: string) => {
    setKeywords(prev => prev.includes(kw) ? prev.filter(k => k !== kw) : [...prev, kw])
  }

  const attach = () => {
    if (!onAttachToGraph || !query.trim()) return
    const seed = createNode(
      mode === 'plate' ? 'plate' : mode === 'phone' ? 'phone' : mode === 'person' ? 'person' : 'username',
      query.trim(),
      { source: 'general_search' },
    )
    const nodes: NodeData[] = [seed]
    const edges: EdgeData[] = []
    for (const a of assistants) {
      const n = createNode('domain', a.name, { url: a.url, source: 'general_search' })
      nodes.push(n)
      edges.push(createEdge(seed.id, n.id, 'linked_to'))
    }
    onAttachToGraph(nodes, edges)
    onClose()
  }

  if (!open) return null

  return (
    <div className="general-search-overlay" role="dialog" aria-modal="true">
      <div className="general-search-panel">
        <header className="general-search-header">
          <div>
            <h2>{t('generalSearch.title')}</h2>
            <p>{t('generalSearch.subtitle')}</p>
          </div>
          <button type="button" className="general-search-close" onClick={onClose} aria-label={t('generalSearch.close')}>
            <X size={18} />
          </button>
        </header>

        <div className="general-search-tabs">
          {modeTabs.map(tab => (
            <button
              key={tab.id}
              type="button"
              className={mode === tab.id ? 'active' : ''}
              onClick={() => setMode(tab.id)}
            >
              <tab.icon size={13} /> {tab.label}
            </button>
          ))}
        </div>

        <div className="general-search-form">
          <input
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder={t(`generalSearch.placeholder.${mode}`)}
          />
          <button type="button" className="btn btn-primary" onClick={runSearch} disabled={loading}>
            {loading ? t('generalSearch.searching') : t('generalSearch.run')}
          </button>
        </div>

        {mode === 'forum' && (
          <div className="general-search-keywords">
            <span className="general-search-kw-label">{t('generalSearch.keywords')}</span>
            {FORUM_PRESETS.map(kw => (
              <button
                key={kw}
                type="button"
                className={`kw-chip ${keywords.includes(kw) ? 'on' : ''}`}
                onClick={() => toggleKeyword(kw)}
              >
                {kw}
              </button>
            ))}
          </div>
        )}

        <ul className="general-search-results">
          {assistants.map(a => (
            <li key={a.id}>
              <span>{a.name}</span>
              <a href={a.url} target="_blank" rel="noopener noreferrer">
                <ExternalLink size={12} /> {t('generalSearch.open')}
              </a>
            </li>
          ))}
        </ul>

        {disclaimer && <p className="general-search-disclaimer">{disclaimer}</p>}

        <footer className="general-search-footer">
          {onAttachToGraph && assistants.length > 0 && (
            <button type="button" className="btn btn-primary" onClick={attach}>
              {t('generalSearch.attachGraph')}
            </button>
          )}
          <button type="button" className="btn btn-ghost" onClick={onClose}>{t('generalSearch.close')}</button>
        </footer>
      </div>
    </div>
  )
}
