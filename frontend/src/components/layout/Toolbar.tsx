import React, { useState } from 'react'
import {
  GitGraph, Plus, Upload, Save, LayoutGrid, ZoomIn, ZoomOut,
  Maximize2, Undo, Redo, Search, ChevronLeft, ChevronRight,
  Layers, Play, Cpu
} from 'lucide-react'
import { useGraphStore } from '../../graph/graphStore'
import { ImportModal } from '../modals/ImportModal'
import { apiClient } from '../../services/api'
import './Toolbar.css'

interface ToolbarProps {
  leftCollapsed: boolean
  rightCollapsed: boolean
  onToggleLeft: () => void
  onToggleRight: () => void
}

export const Toolbar: React.FC<ToolbarProps> = ({
  leftCollapsed, rightCollapsed, onToggleLeft, onToggleRight
}) => {
  const { layoutType, setLayout, undo, redo, clearGraph, history, historyIndex,
    currentWorkspace, nodes, edges } = useGraphStore()
  const [showImport, setShowImport] = useState(false)
  const [saving, setSaving] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  const handleSave = async () => {
    setSaving(true)
    try {
      await apiClient.post(`/graph/${currentWorkspace}`, { nodes, edges })
    } catch {/* fallback: save to localStorage */
      localStorage.setItem(`osintgraph:${currentWorkspace}`, JSON.stringify({ nodes, edges }))
    } finally {
      setSaving(false)
    }
  }

  const canUndo = historyIndex > 0
  const canRedo = historyIndex < history.length - 1

  return (
    <>
      <div className="toolbar">
        {/* Brand */}
        <div className="toolbar-brand">
          <GitGraph size={18} className="brand-icon" />
          <span className="brand-name">OSINTGraph</span>
          <span className="brand-workspace">{currentWorkspace}</span>
        </div>

        <div className="toolbar-divider" />

        {/* Panel toggles */}
        <button className="btn btn-ghost toolbar-btn" onClick={onToggleLeft}
          data-tooltip={leftCollapsed ? 'Show entity panel' : 'Hide entity panel'}>
          <ChevronLeft size={14} style={{ transform: leftCollapsed ? 'rotate(180deg)' : undefined }} />
          <Layers size={14} />
        </button>

        <div className="toolbar-divider" />

        {/* History */}
        <button className="btn btn-ghost toolbar-btn" onClick={undo} disabled={!canUndo}
          data-tooltip="Undo (Ctrl+Z)">
          <Undo size={14} />
        </button>
        <button className="btn btn-ghost toolbar-btn" onClick={redo} disabled={!canRedo}
          data-tooltip="Redo (Ctrl+Y)">
          <Redo size={14} />
        </button>

        <div className="toolbar-divider" />

        {/* Layout picker */}
        <div className="layout-group">
          <button className={`btn toolbar-btn ${layoutType === 'force' ? 'active' : 'btn-ghost'}`}
            onClick={() => setLayout('force')} data-tooltip="Force-directed layout">
            <Cpu size={14} />
          </button>
          <button className={`btn toolbar-btn ${layoutType === 'hierarchical' ? 'active' : 'btn-ghost'}`}
            onClick={() => setLayout('hierarchical')} data-tooltip="Hierarchical layout">
            <GitGraph size={14} />
          </button>
          <button className={`btn toolbar-btn ${layoutType === 'grid' ? 'active' : 'btn-ghost'}`}
            onClick={() => setLayout('grid')} data-tooltip="Grid layout">
            <LayoutGrid size={14} />
          </button>
        </div>

        <div className="toolbar-divider" />

        {/* Actions */}
        <button className="btn btn-ghost toolbar-btn" onClick={() => setShowImport(true)}
          data-tooltip="Import CSV / JSON">
          <Upload size={14} />
          <span>Import</span>
        </button>

        <button className={`btn btn-ghost toolbar-btn ${saving ? 'loading' : ''}`}
          onClick={handleSave} data-tooltip="Save graph">
          <Save size={14} className={saving ? 'loading-spin' : ''} />
          <span>Save</span>
        </button>

        <div className="toolbar-divider" />

        {/* Search */}
        <div className="toolbar-search">
          <Search size={12} className="search-icon" />
          <input
            type="text"
            placeholder="Search nodes…"
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="toolbar-spacer" />

        {/* Stats */}
        <div className="toolbar-stats">
          <span>{nodes.length} nodes</span>
          <span className="stat-sep">·</span>
          <span>{edges.length} edges</span>
        </div>

        {/* Right toggle */}
        <button className="btn btn-ghost toolbar-btn" onClick={onToggleRight}
          data-tooltip={rightCollapsed ? 'Show inspector' : 'Hide inspector'}>
          <ChevronRight size={14} style={{ transform: rightCollapsed ? 'rotate(180deg)' : undefined }} />
        </button>
      </div>

      {showImport && <ImportModal onClose={() => setShowImport(false)} />}
    </>
  )
}
