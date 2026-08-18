import React, { useState, useCallback } from 'react'
import { X, Search, Loader, Shield, AlertTriangle } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import {
  searchDeathRecords,
  isClientDeathSearchAvailable,
  type DeathRecord,
  type DeathSearchParams,
} from '../../services/deathSearch'
import { ActRequestButtons } from './ActRequestButtons'
import './DeathSearchModal.css'

interface DeathSearchModalProps {
  onClose: () => void
  initialLastName?: string
  initialFirstName?: string
}

function splitPersonLabel(label: string): { lastName: string; firstName: string } {
  const trimmed = label.trim()
  if (!trimmed) return { lastName: '', firstName: '' }
  if (trimmed.includes(',')) {
    const [last, first] = trimmed.split(',', 2).map(s => s.trim())
    return { lastName: last ?? '', firstName: first ?? '' }
  }
  const tokens = trimmed.split(/\s+/)
  if (tokens.length === 1) return { lastName: tokens[0], firstName: '' }
  if (tokens[tokens.length - 1] === tokens[tokens.length - 1].toUpperCase()) {
    return { lastName: tokens[tokens.length - 1], firstName: tokens.slice(0, -1).join(' ') }
  }
  return { lastName: tokens[0], firstName: tokens.slice(1).join(' ') }
}

export const DeathSearchModal: React.FC<DeathSearchModalProps> = ({
  onClose,
  initialLastName = '',
  initialFirstName = '',
}) => {
  const { t } = useTranslation()
  const parsed = splitPersonLabel(
    initialLastName && !initialFirstName ? initialLastName : `${initialFirstName} ${initialLastName}`.trim()
  )

  const [lastName, setLastName] = useState(parsed.lastName || initialLastName)
  const [firstName, setFirstName] = useState(parsed.firstName || initialFirstName)
  const [birthYearFrom, setBirthYearFrom] = useState('')
  const [birthYearTo, setBirthYearTo] = useState('')
  const [commune, setCommune] = useState('')
  const [departement, setDepartement] = useState('')
  const [loading, setLoading] = useState(false)
  const [records, setRecords] = useState<DeathRecord[]>([])
  const [log, setLog] = useState<string[]>([])
  const [searched, setSearched] = useState(false)

  const clientMode = isClientDeathSearchAvailable()

  const handleSearch = useCallback(async () => {
    if (!lastName.trim()) return
    setLoading(true)
    setSearched(true)
    setRecords([])
    setLog([])

    const params: DeathSearchParams = {
      lastName: lastName.trim(),
      firstName: firstName.trim() || undefined,
      birthYearFrom: birthYearFrom ? Number(birthYearFrom) : undefined,
      birthYearTo: birthYearTo ? Number(birthYearTo) : undefined,
      commune: commune.trim() || undefined,
      departement: departement.trim() || undefined,
    }

    try {
      const result = await searchDeathRecords(params)
      setRecords(result.records)
      setLog(result.log)
    } finally {
      setLoading(false)
    }
  }, [lastName, firstName, birthYearFrom, birthYearTo, commune, departement])

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-panel death-search-modal fade-in" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-title">
            <Search size={16} /> {t('deathSearch.title')}
          </div>
          <button className="btn btn-ghost icon-btn" onClick={onClose} aria-label={t('deathSearch.close')}>
            <X size={14} />
          </button>
        </div>

        <div className="modal-body">
          <p className="death-search-intro">{t('deathSearch.intro')}</p>

          {clientMode ? (
            <div className="death-search-privacy">
              <Shield size={14} />
              <span>{t('deathSearch.clientMode')}</span>
            </div>
          ) : (
            <div className="death-search-privacy death-search-privacy-backend">
              <AlertTriangle size={14} />
              <span>{t('deathSearch.backendMode')}</span>
            </div>
          )}

          <div className="death-search-form">
            <div className="form-row">
              <label>
                {t('deathSearch.lastName')}
                <input
                  type="text"
                  value={lastName}
                  onChange={e => setLastName(e.target.value)}
                  placeholder="DUPONT"
                  autoFocus
                />
              </label>
              <label>
                {t('deathSearch.firstName')}
                <input
                  type="text"
                  value={firstName}
                  onChange={e => setFirstName(e.target.value)}
                  placeholder="Jean"
                />
              </label>
            </div>
            <div className="form-row">
              <label>
                {t('deathSearch.birthYearFrom')}
                <input
                  type="number"
                  value={birthYearFrom}
                  onChange={e => setBirthYearFrom(e.target.value)}
                  placeholder="1920"
                  min={1800}
                  max={2100}
                />
              </label>
              <label>
                {t('deathSearch.birthYearTo')}
                <input
                  type="number"
                  value={birthYearTo}
                  onChange={e => setBirthYearTo(e.target.value)}
                  placeholder="1960"
                  min={1800}
                  max={2100}
                />
              </label>
            </div>
            <div className="form-row">
              <label>
                {t('deathSearch.commune')}
                <input
                  type="text"
                  value={commune}
                  onChange={e => setCommune(e.target.value)}
                  placeholder="Paris"
                />
              </label>
              <label>
                {t('deathSearch.departement')}
                <input
                  type="text"
                  value={departement}
                  onChange={e => setDepartement(e.target.value)}
                  placeholder="75"
                  maxLength={3}
                />
              </label>
            </div>
          </div>

          <button
            className="btn btn-primary death-search-submit"
            onClick={handleSearch}
            disabled={loading || !lastName.trim()}
          >
            {loading ? <Loader size={14} className="spin" /> : <Search size={14} />}
            {loading ? t('deathSearch.searching') : t('deathSearch.search')}
          </button>

          {searched && !loading && records.length === 0 && (
            <p className="death-search-empty">{t('deathSearch.noResults')}</p>
          )}

          {records.length > 0 && (
            <div className="death-search-results">
              <p className="death-search-count">
                {t('deathSearch.resultsCount', { count: records.length })}
              </p>
              <div className="death-search-table-wrap">
                <table className="death-search-table">
                  <thead>
                    <tr>
                      <th>{t('deathSearch.colName')}</th>
                      <th>{t('deathSearch.colBirth')}</th>
                      <th>{t('deathSearch.colBirthPlace')}</th>
                      <th>{t('deathSearch.colDeath')}</th>
                      <th>{t('deathSearch.colActions')}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {records.map((r, i) => (
                      <tr key={`${r.label}-${i}`}>
                        <td>
                          <strong>{r.nom}</strong>
                          <span className="death-search-prenoms">{r.prenoms.replace(/,/g, ' ')}</span>
                        </td>
                        <td>{r.date_naissance || '—'}</td>
                        <td>{r.commune_naissance || r.pays_naissance || '—'}</td>
                        <td>{r.date_deces || '—'}</td>
                        <td>
                          <ActRequestButtons record={r} />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <p className="death-search-disclaimer">{t('deathSearch.disclaimer')}</p>
            </div>
          )}

          {log.length > 0 && (
            <details className="death-search-log">
              <summary>{t('deathSearch.log')}</summary>
              <pre>{log.join('\n')}</pre>
            </details>
          )}
        </div>
      </div>
    </div>
  )
}
