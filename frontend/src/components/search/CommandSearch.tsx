import React, { useEffect, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Search } from 'lucide-react'
import { apiClient } from '../../services/api'
import type { SearchResult } from '../../types/domain'
import './CommandSearch.css'

export const CommandSearch: React.FC = () => {
  const { t } = useTranslation()
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const navigate = useNavigate()

  const search = useCallback(async (q: string) => {
    if (!q.trim()) {
      setResults([])
      return
    }
    const res = await apiClient.get(`/api/v1/search?q=${encodeURIComponent(q)}`)
    if (res.ok && res.data) {
      setResults(res.data as SearchResult[])
    }
  }, [])

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        setOpen(v => !v)
      }
      if (e.key === 'Escape') setOpen(false)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [])

  useEffect(() => {
    const t = setTimeout(() => search(query), 200)
    return () => clearTimeout(t)
  }, [query, search])

  const selectResult = (r: SearchResult) => {
    setOpen(false)
    setQuery('')
    if (r.entity_type === 'PERSON') {
      navigate(`/dossier/${r.dossier_id}/person/${r.id}`)
    } else {
      navigate(`/dossier/${r.dossier_id}`)
    }
  }

  const matchTypeKey = (matchType: SearchResult['match_type']) =>
    `commandSearch.match${matchType.charAt(0).toUpperCase()}${matchType.slice(1)}` as const

  if (!open) return null

  return (
    <div className="command-search-overlay" onClick={() => setOpen(false)}>
      <div className="command-search glass-panel" onClick={e => e.stopPropagation()}>
        <div className="command-search-input">
          <Search size={16} />
          <input
            autoFocus
            placeholder={t('commandSearch.placeholder')}
            value={query}
            onChange={e => setQuery(e.target.value)}
          />
          <kbd>Esc</kbd>
        </div>
        <ul className="command-search-results">
          {results.length === 0 && query && <li className="empty">{t('commandSearch.noResults')}</li>}
          {results.map(r => (
            <li key={r.id} onClick={() => selectResult(r)}>
              <span className="result-label">{r.label}</span>
              <span className="result-type">{r.entity_type}</span>
              <span className="result-dossier">{r.dossier_name}</span>
              <span className={`match-type match-${r.match_type}`}>
                {t(matchTypeKey(r.match_type))}
              </span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
