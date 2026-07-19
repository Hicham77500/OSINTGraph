import React from 'react'
import { X, Download, FileJson, FileText, FileSpreadsheet } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { useGraphStore } from '../../graph/graphStore'
import { exportToJson, exportToCsv, exportToMarkdown, downloadStringAsFile } from '../../utils/exportUtils'
import './ImportModal.css'

interface ExportModalProps {
  onClose: () => void
}

export const ExportModal: React.FC<ExportModalProps> = ({ onClose }) => {
  const { nodes, edges, currentWorkspace } = useGraphStore()
  const { t } = useTranslation()

  const handleExportJson = () => {
    const json = exportToJson(nodes, edges)
    downloadStringAsFile(json, `${currentWorkspace}_export.json`, 'application/json')
    onClose()
  }

  const handleExportCsv = () => {
    const csv = exportToCsv(nodes, edges)
    downloadStringAsFile(csv, `${currentWorkspace}_nodes.csv`, 'text/csv')
    onClose()
  }

  const handleExportMd = () => {
    const md = exportToMarkdown(nodes, edges)
    downloadStringAsFile(md, `${currentWorkspace}_export.md`, 'text/markdown')
    onClose()
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-panel fade-in" onClick={e => e.stopPropagation()} style={{ maxWidth: '400px' }}>
        <div className="modal-header">
          <div className="modal-title"><Download size={16} /> {t('exportModal.title')}</div>
          <button className="btn btn-ghost icon-btn" onClick={onClose}><X size={14} /></button>
        </div>

        <div className="modal-body" style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <p style={{ margin: '0 0 10px 0', color: 'var(--text-secondary)' }}>
            {t('exportModal.description')}
          </p>
          <button className="btn btn-primary" onClick={handleExportJson} style={{ display: 'flex', gap: '10px', justifyContent: 'flex-start' }}>
            <FileJson size={16} /> {t('exportModal.json')}
          </button>
          <button className="btn btn-ghost" onClick={handleExportCsv} style={{ display: 'flex', gap: '10px', justifyContent: 'flex-start', border: '1px solid var(--border-color)' }}>
            <FileSpreadsheet size={16} /> {t('exportModal.csv')}
          </button>
          <button className="btn btn-ghost" onClick={handleExportMd} style={{ display: 'flex', gap: '10px', justifyContent: 'flex-start', border: '1px solid var(--border-color)' }}>
            <FileText size={16} /> {t('exportModal.markdown')}
          </button>
        </div>

        <div className="modal-footer">
          <button className="btn btn-ghost" onClick={onClose}>{t('importModal.cancel')}</button>
        </div>
      </div>
    </div>
  )
}
