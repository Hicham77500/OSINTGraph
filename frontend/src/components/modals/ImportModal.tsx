import React, { useState, useRef } from 'react'
import { X, Upload, FileText, Table } from 'lucide-react'
import { useGraphStore } from '../../graph/graphStore'
import { NodeType, ALL_NODE_TYPES } from '../../graph/nodeTypes'
import './ImportModal.css'

interface ImportModalProps {
  onClose: () => void
}

export const ImportModal: React.FC<ImportModalProps> = ({ onClose }) => {
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string[][]>([])
  const [columns, setColumns] = useState<Record<number, NodeType | ''>>({})
  const [labelCol, setLabelCol] = useState<number>(0)
  const fileRef = useRef<HTMLInputElement>(null)
  const { addNode } = useGraphStore()

  const handleFile = (f: File) => {
    setFile(f)
    const reader = new FileReader()
    reader.onload = (e) => {
      const text = e.target?.result as string
      if (f.name.endsWith('.json')) {
        try {
          const json = JSON.parse(text)
          const arr = Array.isArray(json) ? json : [json]
          const rows = arr.map(obj => Object.values(obj).map(String))
          const headers = arr.length > 0 ? Object.keys(arr[0]) : []
          setPreview([headers, ...rows.slice(0, 5)])
        } catch { setPreview([]) }
      } else {
        const rows = text.split('\n').slice(0, 6).map(r => r.split(',').map(c => c.trim().replace(/^"|"$/g, '')))
        setPreview(rows)
      }
    }
    reader.readAsText(f)
  }

  const handleImport = () => {
    if (preview.length < 2) return
    const [headers, ...rows] = preview
    rows.forEach(row => {
      const mainCol = row[labelCol]
      const type: NodeType = (columns[labelCol] as NodeType) || 'domain'
      if (mainCol?.trim()) addNode(type, mainCol.trim())
    })
    onClose()
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-panel fade-in" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-title"><Upload size={16} /> Import Data</div>
          <button className="btn btn-ghost icon-btn" onClick={onClose}><X size={14} /></button>
        </div>

        <div className="modal-body">
          {/* Drop zone */}
          <div className="drop-zone"
            onDragOver={e => e.preventDefault()}
            onDrop={e => { e.preventDefault(); const f = e.dataTransfer.files[0]; if (f) handleFile(f) }}
            onClick={() => fileRef.current?.click()}>
            <input ref={fileRef} type="file" accept=".csv,.json" style={{ display: 'none' }}
              onChange={e => { if (e.target.files?.[0]) handleFile(e.target.files[0]) }} />
            <FileText size={32} className="drop-icon" />
            {file ? (
              <div className="drop-file-name">{file.name}</div>
            ) : (
              <>
                <div className="drop-label">Drop a CSV or JSON file</div>
                <div className="drop-sub">or click to browse</div>
              </>
            )}
          </div>

          {/* Preview */}
          {preview.length > 0 && (
            <div className="preview-section">
              <div className="section-label" style={{ padding: '10px 0 4px' }}>Preview & Column Mapping</div>
              <div className="preview-table-wrap">
                <table className="preview-table">
                  <thead>
                    <tr>
                      {preview[0].map((_, i) => (
                        <th key={i}>
                          <select value={columns[i] ?? ''}
                            onChange={e => setColumns(c => ({ ...c, [i]: e.target.value as NodeType | '' }))}
                            style={{ width: '100%' }}>
                            <option value="">— ignore —</option>
                            {ALL_NODE_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
                          </select>
                        </th>
                      ))}
                    </tr>
                    <tr>
                      {preview[0].map((header, i) => (
                        <th key={i} className="col-header">{header}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {preview.slice(1).map((row, ri) => (
                      <tr key={ri}>
                        {row.map((cell, ci) => <td key={ci}>{cell}</td>)}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button className="btn btn-ghost" onClick={onClose}>Cancel</button>
          <button className="btn btn-primary" onClick={handleImport} disabled={preview.length < 2}>
            Import nodes
          </button>
        </div>
      </div>
    </div>
  )
}
