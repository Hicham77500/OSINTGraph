import React, { useEffect, useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, ChevronRight, GitGraph, Pencil, Plus, Trash2 } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { useInvestigationStore } from '../stores/investigationStore'
import { apiClient } from '../services/api'
import type { Carnet, Entity, Observation } from '../types/domain'
import { carnetDescriptionKey, carnetIcon } from '../utils/carnetMeta'
import {
  collectNoteItems,
  formatNoteDate,
  type NoteItem,
} from '../utils/noteHelpers'
import './DossiersPage.css'
import './CarnetViewPage.css'

const NOTEBOOK_ENTITY_TYPES: Record<string, string[]> = {
  personnes: ['PERSON'],
  reseaux_sociaux: ['SOCIAL_ACCOUNT', 'USERNAME'],
  entreprises: ['ORGANIZATION'],
  pseudonymes: ['ALIAS', 'USERNAME'],
}

type TimelineEntry = {
  id: string
  observedAt: string
  entityLabel: string
  entityId: string
  summary: string
  platform: string
}

function filterEntitiesByNotebook(entities: Entity[], notebookType: string): Entity[] {
  const allowed = NOTEBOOK_ENTITY_TYPES[notebookType]
  if (!allowed || allowed.length === 0) return entities
  return entities.filter(e => allowed.includes(e.entity_type))
}

function observationSummary(obs: Observation): string {
  const content = obs.content
  if (typeof content.value === 'string') return content.value
  if (typeof content.field === 'string') return content.field
  return JSON.stringify(content)
}

export const CarnetViewPage: React.FC = () => {
  const { dossierId, carnetId } = useParams<{ dossierId: string; carnetId: string }>()
  const { t, i18n } = useTranslation()
  const {
    currentDossier, carnets, entities,
    fetchDossier, fetchCarnets, fetchEntities, createEntity,
    updateEntity, deleteEntity,
  } = useInvestigationStore()
  const [timeline, setTimeline] = useState<TimelineEntry[]>([])
  const [notes, setNotes] = useState<NoteItem[]>([])
  const [loadingObs, setLoadingObs] = useState(false)
  const [noteTitle, setNoteTitle] = useState('')
  const [noteBody, setNoteBody] = useState('')
  const [savingNote, setSavingNote] = useState(false)
  const [quickUsername, setQuickUsername] = useState('')
  const [addingUsername, setAddingUsername] = useState(false)
  const [editingNote, setEditingNote] = useState<NoteItem | null>(null)
  const [editTitle, setEditTitle] = useState('')
  const [editBody, setEditBody] = useState('')
  const [savingEdit, setSavingEdit] = useState(false)
  const [deletingNoteId, setDeletingNoteId] = useState<string | null>(null)

  const carnet = useMemo(
    () => carnets.find(c => c.id === carnetId) ?? null,
    [carnets, carnetId],
  )

  const filteredEntities = useMemo(
    () => (carnet ? filterEntitiesByNotebook(entities, carnet.notebook_type) : []),
    [entities, carnet],
  )

  const locale = i18n.language.startsWith('fr') ? 'fr-FR' : 'en-US'

  useEffect(() => {
    if (!dossierId || !carnetId) return
    fetchDossier(dossierId)
    fetchCarnets(dossierId)
    fetchEntities(dossierId, carnetId)
  }, [dossierId, carnetId, fetchDossier, fetchCarnets, fetchEntities])

  useEffect(() => {
    if (!carnet) return
    if (carnet.notebook_type !== 'chronologie' && carnet.notebook_type !== 'notes') return

    let cancelled = false
    setLoadingObs(true)

    const entityList = carnet.notebook_type === 'notes' ? entities : filteredEntities

    if (entityList.length === 0) {
      setTimeline([])
      setNotes([])
      setLoadingObs(false)
      return
    }

    Promise.all(
      entityList.map(async entity => {
        const res = await apiClient.get(`/api/v1/entities/${entity.id}/observations`)
        const obs = res.ok ? (res.data as Observation[]) : []
        return { entity, obs }
      }),
    ).then(results => {
      if (cancelled) return

      if (carnet.notebook_type === 'chronologie') {
        const entries: TimelineEntry[] = []
        for (const { entity, obs } of results) {
          for (const o of obs) {
            entries.push({
              id: o.id,
              observedAt: o.observed_at,
              entityLabel: entity.label,
              entityId: entity.id,
              summary: observationSummary(o),
              platform: o.platform,
            })
          }
        }
        entries.sort((a, b) => new Date(b.observedAt).getTime() - new Date(a.observedAt).getTime())
        setTimeline(entries)
      }

      if (carnet.notebook_type === 'notes') {
        const obsMap = new Map(results.map(r => [r.entity.id, r.obs]))
        setNotes(collectNoteItems(entityList, obsMap))
      }

      setLoadingObs(false)
    })

    return () => { cancelled = true }
  }, [carnet, entities, filteredEntities])

  if (!dossierId || !carnetId) return null

  const graphPath = `/dossier/${dossierId}/graph`
  const dossierName = currentDossier?.name ?? t('dossier.title')

  const handleCreateNote = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!noteBody.trim() || !carnetId) return
    setSavingNote(true)
    const title = noteTitle.trim() || t('carnetView.untitledNote')
    await createEntity(dossierId, {
      entity_type: 'CUSTOM',
      label: title,
      carnet_id: carnetId,
      properties: { title, content: noteBody.trim() },
    })
    setNoteTitle('')
    setNoteBody('')
    setSavingNote(false)
  }

  const openEditNote = (note: NoteItem) => {
    setEditingNote(note)
    setEditTitle(note.title)
    setEditBody(note.text)
  }

  const handleSaveEdit = async () => {
    if (!editingNote || !editBody.trim() || !carnetId) return
    setSavingEdit(true)
    const title = editTitle.trim() || t('carnetView.untitledNote')
    await updateEntity(
      editingNote.entityId,
      { label: title, properties: { title, content: editBody.trim() } },
      dossierId,
      carnetId,
    )
    setSavingEdit(false)
    setEditingNote(null)
  }

  const handleDeleteNote = async (entityId: string) => {
    if (!carnetId) return
    if (!window.confirm(t('carnetView.deleteNoteConfirm'))) return
    setDeletingNoteId(entityId)
    await deleteEntity(entityId, dossierId, carnetId)
    setDeletingNoteId(null)
  }

  const handleQuickAddUsername = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!quickUsername.trim() || !carnetId) return
    setAddingUsername(true)
    await createEntity(dossierId, {
      entity_type: 'USERNAME',
      label: quickUsername.trim(),
      carnet_id: carnetId,
      properties: { platform: 'unknown' },
    })
    setQuickUsername('')
    setAddingUsername(false)
  }

  const renderNoteDates = (note: NoteItem) => (
    <div className="note-meta">
      <span>{t('carnetView.createdAt', { date: formatNoteDate(note.createdAt, locale) })}</span>
      {note.updatedAt !== note.createdAt && (
        <span>{t('carnetView.updatedAt', { date: formatNoteDate(note.updatedAt, locale) })}</span>
      )}
      {note.observedAt && (
        <span>{t('carnetView.datedAt', { date: formatNoteDate(note.observedAt, locale) })}</span>
      )}
    </div>
  )

  const renderEmptyState = (
    titleKey: string,
    descKey: string,
    showGraphCta = true,
    extra?: React.ReactNode,
  ) => (
    <div className="carnet-empty-state glass-panel">
      <h3>{t(titleKey)}</h3>
      <p>{t(descKey)}</p>
      {extra}
      {showGraphCta && (
        <Link to={graphPath} className="btn btn-primary carnet-empty-cta">
          <GitGraph size={16} />
          {t('carnetView.goToGraph')}
        </Link>
      )}
    </div>
  )

  const renderEntityCard = (entity: Entity) => {
    const isPerson = entity.entity_type === 'PERSON'
    const card = (
      <>
        <div className="entity-card-main">
          <span className="entity-card-label">{entity.label}</span>
          <span className="entity-card-type">{entity.entity_type}</span>
        </div>
        <div className="entity-card-badges">
          <span className={`badge badge-${entity.status.toLowerCase()}`}>{entity.status}</span>
          <span className="badge">{Math.round(entity.confidence * 100)}%</span>
        </div>
      </>
    )

    if (isPerson) {
      return (
        <Link
          key={entity.id}
          to={`/dossier/${dossierId}/person/${entity.id}`}
          className="entity-card glass-panel"
        >
          {card}
        </Link>
      )
    }

    return (
      <div key={entity.id} className="entity-card entity-card-static glass-panel">
        {card}
      </div>
    )
  }

  const renderContent = (c: Carnet) => {
    if (c.notebook_type === 'chronologie') {
      if (loadingObs) return <p className="carnet-empty">{t('carnetView.loading')}</p>
      if (timeline.length === 0) {
        return renderEmptyState(
          'carnetView.emptyTimelineTitle',
          'carnetView.emptyTimelineDesc',
        )
      }
      return (
        <ul className="timeline-list">
          {timeline.map(entry => (
            <li key={entry.id} className="timeline-item">
              <time className="timeline-date">
                {new Date(entry.observedAt).toLocaleDateString()}
              </time>
              <div className="timeline-content">
                <strong>{entry.entityLabel}</strong> — {entry.platform}: {entry.summary}
              </div>
            </li>
          ))}
        </ul>
      )
    }

    if (c.notebook_type === 'notes') {
      return (
        <div className="notes-section">
          <form className="note-form glass-panel" onSubmit={handleCreateNote}>
            <h3 className="note-form-title">
              <Plus size={16} />
              {t('carnetView.newNote')}
            </h3>
            <input
              value={noteTitle}
              onChange={e => setNoteTitle(e.target.value)}
              placeholder={t('carnetView.noteTitlePlaceholder')}
            />
            <textarea
              value={noteBody}
              onChange={e => setNoteBody(e.target.value)}
              placeholder={t('carnetView.noteBodyPlaceholder')}
              rows={4}
              required
            />
            <button
              type="submit"
              className="btn btn-primary"
              disabled={savingNote || !noteBody.trim()}
            >
              {savingNote ? t('carnetView.savingNote') : t('carnetView.saveNote')}
            </button>
          </form>

          {loadingObs ? (
            <p className="carnet-empty">{t('carnetView.loading')}</p>
          ) : notes.length === 0 ? (
            <p className="notes-hint">{t('carnetView.emptyNotesHint')}</p>
          ) : (
            <div className="notes-list">
              {notes.map(note => (
                <div key={note.entityId} className="note-item glass-panel">
                  <div className="note-item-header">
                    <div className="note-item-title-block">
                      <div className="note-entity">{note.title}</div>
                      {renderNoteDates(note)}
                    </div>
                    <div className="note-item-actions">
                      <button
                        type="button"
                        className="btn-icon"
                        title={t('carnetView.editNote')}
                        onClick={() => openEditNote(note)}
                      >
                        <Pencil size={15} />
                      </button>
                      <button
                        type="button"
                        className="btn-icon btn-icon-danger"
                        title={t('carnetView.deleteNote')}
                        disabled={deletingNoteId === note.entityId}
                        onClick={() => handleDeleteNote(note.entityId)}
                      >
                        <Trash2 size={15} />
                      </button>
                    </div>
                  </div>
                  <p className="note-text">{note.text}</p>
                </div>
              ))}
            </div>
          )}

          {editingNote && (
            <div className="modal-overlay" onClick={() => setEditingNote(null)}>
              <div className="modal glass-panel note-edit-modal" onClick={e => e.stopPropagation()}>
                <h3>{t('carnetView.editNote')}</h3>
                <input
                  value={editTitle}
                  onChange={e => setEditTitle(e.target.value)}
                  placeholder={t('carnetView.noteTitlePlaceholder')}
                />
                <textarea
                  value={editBody}
                  onChange={e => setEditBody(e.target.value)}
                  rows={6}
                  required
                />
                <div className="modal-actions">
                  <button className="btn btn-ghost" onClick={() => setEditingNote(null)}>
                    {t('carnetView.cancelEdit')}
                  </button>
                  <button
                    className="btn btn-primary"
                    disabled={savingEdit || !editBody.trim()}
                    onClick={handleSaveEdit}
                  >
                    {savingEdit ? t('carnetView.savingNote') : t('carnetView.saveChanges')}
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )
    }

    if (filteredEntities.length === 0) {
      const descKey = `carnetView.emptyEntitiesDesc.${c.notebook_type}`
      const quickAdd = c.notebook_type === 'reseaux_sociaux' ? (
        <form className="quick-add-form" onSubmit={handleQuickAddUsername}>
          <label htmlFor="quick-username">{t('carnetView.quickAddUsername')}</label>
          <div className="quick-add-row">
            <input
              id="quick-username"
              value={quickUsername}
              onChange={e => setQuickUsername(e.target.value)}
              placeholder={t('carnetView.usernamePlaceholder')}
            />
            <button
              type="submit"
              className="btn btn-primary"
              disabled={addingUsername || !quickUsername.trim()}
            >
              {t('carnetView.addEntity')}
            </button>
          </div>
        </form>
      ) : undefined

      return renderEmptyState(
        'carnetView.emptyEntitiesTitle',
        descKey,
        true,
        quickAdd,
      )
    }

    return (
      <div className="entity-list">
        {filteredEntities.map(renderEntityCard)}
      </div>
    )
  }

  return (
    <div className="workspace-page">
      <nav className="breadcrumb" aria-label="Breadcrumb">
        <Link to="/">{t('carnetView.breadcrumbDossiers')}</Link>
        <ChevronRight size={14} className="breadcrumb-sep" />
        <Link to={`/dossier/${dossierId}`}>{dossierName}</Link>
        <ChevronRight size={14} className="breadcrumb-sep" />
        <span className="breadcrumb-current">{carnet?.name ?? t('carnetView.title')}</span>
      </nav>

      <header className="carnet-view-header">
        <div className="carnet-view-header-main">
          <div className="carnet-view-title-row">
            {carnet && carnetIcon(carnet.notebook_type, 22)}
            <h1>{carnet?.name ?? t('carnetView.title')}</h1>
          </div>
          {carnet && (
            <p className="carnet-type-label">
              {t(carnetDescriptionKey(carnet.notebook_type), { defaultValue: carnet.notebook_type })}
            </p>
          )}
        </div>
        <Link to={graphPath} className="btn btn-ghost carnet-graph-link">
          <GitGraph size={16} />
          {t('carnetView.openGraph')}
        </Link>
      </header>

      {carnet ? renderContent(carnet) : (
        <p className="carnet-empty">{t('carnetView.loading')}</p>
      )}
    </div>
  )
}
