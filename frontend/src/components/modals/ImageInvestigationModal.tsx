import React, { useCallback, useEffect, useMemo, useState } from 'react'
import {
  X, Upload, Download, ExternalLink, Image as ImageIcon, MapPin, User,
} from 'lucide-react'
import { useTranslation } from 'react-i18next'
import {
  assetDownloadUrl,
  uploadInvestigationImage,
  type VisualSearchAssistant,
  type VisualSearchUploadResult,
} from '../../services/imageInvestigation'
import { createEdge, createNode, type NodeData, type EdgeData } from '../../graph/nodeTypes'
import './ImageInvestigationModal.css'

interface ImageInvestigationModalProps {
  open: boolean
  onClose: () => void
  /** Pre-fill person context */
  linkedPerson?: string
  /** Pre-fill place / location query */
  linkedPlace?: string
  /** When set, merge image + search links into the graph */
  onAttachToGraph?: (nodes: NodeData[], edges: EdgeData[]) => void
}

export const ImageInvestigationModal: React.FC<ImageInvestigationModalProps> = ({
  open,
  onClose,
  linkedPerson: linkedPersonProp = '',
  linkedPlace: linkedPlaceProp = '',
  onAttachToGraph,
}) => {
  const { t } = useTranslation()
  const [linkedPerson, setLinkedPerson] = useState(linkedPersonProp)
  const [linkedPlace, setLinkedPlace] = useState(linkedPlaceProp)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState<VisualSearchUploadResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [activeAssistant, setActiveAssistant] = useState<VisualSearchAssistant | null>(null)

  useEffect(() => {
    if (open) {
      setLinkedPerson(linkedPersonProp)
      setLinkedPlace(linkedPlaceProp)
    }
  }, [open, linkedPersonProp, linkedPlaceProp])

  useEffect(() => {
    return () => {
      if (previewUrl?.startsWith('blob:')) URL.revokeObjectURL(previewUrl)
    }
  }, [previewUrl])

  const onPickFile = useCallback(async (file: File | null) => {
    setError(null)
    setResult(null)
    if (!file) return
    if (previewUrl?.startsWith('blob:')) URL.revokeObjectURL(previewUrl)
    setPreviewUrl(URL.createObjectURL(file))
    setUploading(true)
    const res = await uploadInvestigationImage(file, linkedPerson || undefined, linkedPlace || undefined)
    setUploading(false)
    if (!res.ok || !res.data) {
      setError(res.error ?? t('imageInvestigation.uploadError'))
      return
    }
    setResult(res.data)
    if (res.data.assistants.length > 0) {
      setActiveAssistant(res.data.assistants[0])
    }
  }, [linkedPerson, linkedPlace, previewUrl, t])

  const displayPreview = useMemo(() => {
    if (result?.asset_id) return assetDownloadUrl(result.asset_id)
    return previewUrl
  }, [previewUrl, result?.asset_id])

  const handleAttach = () => {
    if (!result || !onAttachToGraph) return
    const imageNode = createNode('image', result.asset_id, {
      display_name: result.filename,
      asset_id: result.asset_id,
      public_url: result.public_url,
      sha256: result.sha256,
      linked_person: linkedPerson,
      linked_place: linkedPlace,
    })
    const childNodes: NodeData[] = []
    const edges: EdgeData[] = []
    for (const a of result.assistants) {
      const n = createNode('domain', a.name, {
        url: a.url,
        source: 'visual_search',
        method: a.method,
      })
      childNodes.push(n)
      edges.push(createEdge(imageNode.id, n.id, 'linked_to'))
    }
    if (linkedPerson) {
      const p = createNode('person', linkedPerson, { source: 'investigation_context' })
      childNodes.push(p)
      edges.push(createEdge(p.id, imageNode.id, 'linked_to'))
    }
    if (linkedPlace) {
      const loc = createNode('location', linkedPlace, { source: 'investigation_context' })
      childNodes.push(loc)
      edges.push(createEdge(loc.id, imageNode.id, 'linked_to'))
    }
    onAttachToGraph([imageNode, ...childNodes], edges)
    onClose()
  }

  if (!open) return null

  return (
    <div className="image-inv-overlay" role="dialog" aria-modal="true">
      <div className="image-inv-panel">
        <header className="image-inv-header">
          <div>
            <h2>{t('imageInvestigation.title')}</h2>
            <p>{t('imageInvestigation.subtitle')}</p>
          </div>
          <button type="button" className="image-inv-close" onClick={onClose} aria-label={t('imageInvestigation.close')}>
            <X size={18} />
          </button>
        </header>

        <div className="image-inv-context">
          <label>
            <User size={12} /> {t('imageInvestigation.linkedPerson')}
            <input value={linkedPerson} onChange={e => setLinkedPerson(e.target.value)} />
          </label>
          <label>
            <MapPin size={12} /> {t('imageInvestigation.linkedPlace')}
            <input value={linkedPlace} onChange={e => setLinkedPlace(e.target.value)} placeholder={t('imageInvestigation.placePlaceholder')} />
          </label>
        </div>

        <div className="image-inv-workspace">
          <div className="image-inv-preview-col">
            <div className="image-inv-drop">
              <input
                type="file"
                accept="image/jpeg,image/png,image/webp,image/gif"
                onChange={e => onPickFile(e.target.files?.[0] ?? null)}
              />
              <Upload size={20} />
              <span>{uploading ? t('imageInvestigation.uploading') : t('imageInvestigation.dropHint')}</span>
            </div>
            {displayPreview && (
              <div className="image-inv-preview-wrap">
                <img src={displayPreview} alt="" className="image-inv-preview" />
                {result?.asset_id && (
                  <a
                    className="btn btn-ghost image-inv-download"
                    href={assetDownloadUrl(result.asset_id)}
                    download={result.filename}
                  >
                    <Download size={12} /> {t('imageInvestigation.download')}
                  </a>
                )}
              </div>
            )}
          </div>

          <div className="image-inv-browser-col">
            <div className="image-inv-browser-chrome">
              <span className="image-inv-browser-title">
                <ImageIcon size={12} /> {t('imageInvestigation.searchWorkspace')}
              </span>
              {activeAssistant && (
                <a
                  href={activeAssistant.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="image-inv-open-ext"
                >
                  <ExternalLink size={12} /> {t('imageInvestigation.openExternal')}
                </a>
              )}
            </div>
            <p className="image-inv-google-note">{t('imageInvestigation.googleEmbedNote')}</p>
            <ul className="image-inv-assistants">
              {(result?.assistants ?? []).map(a => (
                <li key={a.id}>
                  <button
                    type="button"
                    className={activeAssistant?.id === a.id ? 'active' : ''}
                    onClick={() => setActiveAssistant(a)}
                  >
                    {a.name}
                  </button>
                  <a href={a.url} target="_blank" rel="noopener noreferrer" title={a.hint}>
                    <ExternalLink size={12} />
                  </a>
                </li>
              ))}
            </ul>
            <div className="image-inv-frame">
              {activeAssistant ? (
                <div className="image-inv-frame-inner">
                  <p className="image-inv-frame-hint">{activeAssistant.hint}</p>
                  <a className="btn btn-primary" href={activeAssistant.url} target="_blank" rel="noopener noreferrer">
                    {t('imageInvestigation.launchSearch', { provider: activeAssistant.name })}
                  </a>
                  {linkedPlace && (
                    <a
                      className="image-inv-osm-link"
                      href={`https://www.openstreetmap.org/search?query=${encodeURIComponent(linkedPlace)}`}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      <MapPin size={12} /> {t('imageInvestigation.openOsm', { place: linkedPlace })}
                    </a>
                  )}
                </div>
              ) : (
                <p className="image-inv-frame-empty">{t('imageInvestigation.uploadFirst')}</p>
              )}
            </div>
          </div>
        </div>

        {error && <p className="image-inv-error">{error}</p>}
        {result?.disclaimer && <p className="image-inv-disclaimer">{result.disclaimer}</p>}

        <footer className="image-inv-footer">
          {onAttachToGraph && result && (
            <button type="button" className="btn btn-primary" onClick={handleAttach}>
              {t('imageInvestigation.attachGraph')}
            </button>
          )}
          <button type="button" className="btn btn-ghost" onClick={onClose}>{t('imageInvestigation.close')}</button>
        </footer>
      </div>
    </div>
  )
}
