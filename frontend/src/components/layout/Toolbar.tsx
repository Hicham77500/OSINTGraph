import React, { useState } from 'react'
import {
  GitGraph, Upload, Save, LayoutGrid,
  Undo, Redo, Search, ChevronLeft, ChevronRight,
  Layers, Cpu, Globe, Link2
} from 'lucide-react'
import { useTranslation } from 'react-i18next'
import i18n from '../../i18n'
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
  const { layoutType, setLayout, undo, redo, history, historyIndex,
    currentWorkspace, nodes, edges, connectMode, setConnectMode,
    setSaveStatus, saveStatus } = useGraphStore()
  const { t, i18n: i18nInstance } = useTranslation()
  const currentLang = i18nInstance.language.startsWith('fr') ? 'fr' : 'en'
  const toggleLang = () => i18n.changeLanguage(currentLang === 'fr' ? 'en' : 'fr')
  const [showImport, setShowImport] = useState(false)
  const [saving, setSaving] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  const handleSave = async () => {
    setSaving(true)
    setSaveStatus('saving')
    const res = await apiClient.post(`/graph/${currentWorkspace}`, { nodes, edges })
    if (res.ok) {
      setSaveStatus('saved')
      localStorage.setItem(`osintgraph:${currentWorkspace}`, JSON.stringify({ nodes, edges }))
    } else {
      setSaveStatus('error')
      localStorage.setItem(`osintgraph:${currentWorkspace}`, JSON.stringify({ nodes, edges }))
    }
    setSaving(false)
    setTimeout(() => setSaveStatus('idle'), 2000)
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
          data-tooltip={leftCollapsed ? t('toolbar.showEntityPanel') : t('toolbar.hideEntityPanel')}>
          <ChevronLeft size={14} style={{ transform: leftCollapsed ? 'rotate(180deg)' : undefined }} />
          <Layers size={14} />
        </button>

        <div className="toolbar-divider" />

        {/* History */}
        <button className="btn btn-ghost toolbar-btn" onClick={undo} disabled={!canUndo}
          data-tooltip={t('toolbar.undo')}>
          <Undo size={14} />
        </button>
        <button className="btn btn-ghost toolbar-btn" onClick={redo} disabled={!canRedo}
          data-tooltip={t('toolbar.redo')}>
          <Redo size={14} />
        </button>

        <div className="toolbar-divider" />

        {/* Layout picker */}
        <div className="layout-group">
          <button className={`btn toolbar-btn ${layoutType === 'force' ? 'active' : 'btn-ghost'}`}
            onClick={() => setLayout('force')} data-tooltip={t('toolbar.layoutForce')}>
            <Cpu size={14} />
          </button>
          <button className={`btn toolbar-btn ${layoutType === 'hierarchical' ? 'active' : 'btn-ghost'}`}
            onClick={() => setLayout('hierarchical')} data-tooltip={t('toolbar.layoutHierarchy')}>
            <GitGraph size={14} />
          </button>
          <button className={`btn toolbar-btn ${layoutType === 'grid' ? 'active' : 'btn-ghost'}`}
            onClick={() => setLayout('grid')} data-tooltip={t('toolbar.layoutGrid')}>
            <LayoutGrid size={14} />
          </button>
        </div>

        <div className="toolbar-divider" />

        {/* Connect mode */}
        <button
          className={`btn toolbar-btn ${connectMode ? 'active connect-active' : 'btn-ghost'}`}
          onClick={() => setConnectMode(!connectMode)}
          data-tooltip={t('toolbar.connectTooltip')}
        >
          <Link2 size={14} />
          <span>{t('toolbar.connect')}</span>
        </button>

        <div className="toolbar-divider" />

        {/* Actions */}
        <button className="btn btn-ghost toolbar-btn" onClick={() => setShowImport(true)}
          data-tooltip={t('toolbar.importTooltip')}>
          <Upload size={14} />
          <span>{t('toolbar.import')}</span>
        </button>

        <button className={`btn btn-ghost toolbar-btn ${saving ? 'loading' : ''}`}
          onClick={handleSave} data-tooltip={t('toolbar.saveTooltip')}>
          <Save size={14} className={saving ? 'loading-spin' : ''} />
          <span>{saveStatus === 'saved' ? '✓' : saveStatus === 'error' ? '!' : t('toolbar.save')}</span>
        </button>

        <div className="toolbar-divider" />

        {/* Search */}
        <div className="toolbar-search">
          <Search size={12} className="search-icon" />
          <input
            type="text"
            placeholder={t('toolbar.searchPlaceholder')}
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="toolbar-spacer" />

        {/* Stats */}
        <div className="toolbar-stats">
          <span>{t('toolbar.nodes', { count: nodes.length })}</span>
          <span className="stat-sep">·</span>
          <span>{t('toolbar.edges', { count: edges.length })}</span>
        </div>

        <div className="toolbar-divider" />

        {/* Language switcher */}
        <button
          className="btn btn-ghost toolbar-btn lang-switcher"
          onClick={toggleLang}
          data-tooltip={currentLang === 'fr' ? t('toolbar.switchToEnglish') : t('toolbar.switchToFrench')}
        >
          <Globe size={13} />
          <span className="lang-label">{currentLang.toUpperCase()}</span>
        </button>

        <div className="toolbar-divider" />

        {/* Right toggle */}
        <button className="btn btn-ghost toolbar-btn" onClick={onToggleRight}
          data-tooltip={rightCollapsed ? t('toolbar.showInspector') : t('toolbar.hideInspector')}>
          <ChevronRight size={14} style={{ transform: rightCollapsed ? 'rotate(180deg)' : undefined }} />
        </button>
      </div>

      {showImport && <ImportModal onClose={() => setShowImport(false)} />}
    </>
  )
}
