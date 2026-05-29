import React, { useState } from 'react'
import { NODE_TYPE_CONFIG, EDGE_TYPE_CONFIG } from '../../graph/nodeTypes'
import { useGraphStore } from '../../graph/graphStore'
import { useTranslation } from 'react-i18next'
import { Tag, Clock, Zap, Trash2, ChevronDown, ChevronUp, Copy, ExternalLink } from 'lucide-react'
import { TransformPanel } from './TransformPanel'
import './InspectorPanel.css'

export const InspectorPanel: React.FC = () => {
  const { nodes, edges, selectedNodeId, selectedEdgeId, removeNode, removeEdge } = useGraphStore()
  const { t } = useTranslation()
  const [activeTab, setActiveTab] = useState<'properties' | 'transforms' | 'history'>('properties')

  const selectedNode = nodes.find(n => n.id === selectedNodeId)
  const selectedEdge = edges.find(e => e.id === selectedEdgeId)

  if (!selectedNode && !selectedEdge) {
    return (
      <div className="inspector-panel">
        <div className="panel-header">
          <h3>{t('inspector.title')}</h3>
        </div>
        <div className="inspector-empty">
          <div className="inspector-empty-icon">🔍</div>
          <p>{t('inspector.empty')}</p>
        </div>
      </div>
    )
  }

  // Edge inspector
  if (selectedEdge && !selectedNode) {
    const edgeCfg = EDGE_TYPE_CONFIG[selectedEdge.type]
    const sourceNode = nodes.find(n => n.id === selectedEdge.source)
    const targetNode = nodes.find(n => n.id === selectedEdge.target)
    return (
      <div className="inspector-panel">
        <div className="panel-header">
          <h3>{t('inspector.edgeTitle')}</h3>
          <button className="btn btn-danger icon-btn" onClick={() => removeEdge(selectedEdge.id)}>
            <Trash2 size={12} />
          </button>
        </div>
        <div className="inspector-content">
          <div className="edge-summary">
            <span className="edge-tag" style={{ background: `${edgeCfg.color}22`, color: edgeCfg.color, border: `1px solid ${edgeCfg.color}44` }}>
              {t(`edgeTypes.${selectedEdge.type}` as any, { defaultValue: edgeCfg.label })}
            </span>
            <div className="edge-nodes">
              <span className="edge-node">{sourceNode?.label ?? selectedEdge.source}</span>
              <span className="edge-arrow">→</span>
              <span className="edge-node">{targetNode?.label ?? selectedEdge.target}</span>
            </div>
          </div>
          {selectedEdge.createdAt && (
            <div className="prop-row">
              <span className="prop-key"><Clock size={10} /> {t('inspector.propCreated')}</span>
              <span className="prop-val">{new Date(selectedEdge.createdAt).toLocaleString()}</span>
            </div>
          )}
        </div>
      </div>
    )
  }

  if (!selectedNode) return null
  const cfg = NODE_TYPE_CONFIG[selectedNode.type]

  return (
    <div className="inspector-panel">
      {/* Header */}
      <div className="panel-header">
        <div className="inspector-node-header">
          <span className="inspector-icon" style={{ background: 'transparent' }}>
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="28" height="28" fill="none" stroke={cfg.color} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" dangerouslySetInnerHTML={{ __html: cfg.iconSvg }} />
          </span>
          <div>
            <div className="inspector-node-label">{selectedNode.label}</div>
            <div className="inspector-node-type" style={{ color: cfg.color }}>{t(`nodeTypes.${selectedNode.type}.label`)}</div>
          </div>
        </div>
        <button className="btn btn-danger icon-btn" onClick={() => removeNode(selectedNode.id)}
          data-tooltip={t('inspector.deleteNode')}>
          <Trash2 size={12} />
        </button>
      </div>

      {/* Confidence bar */}
      {selectedNode.metadata?.confidence !== undefined && (
        <div className="confidence-bar-wrapper">
          <div className="confidence-label">
            <span>{t('inspector.confidence')}</span>
            <span>{selectedNode.metadata.confidence}%</span>
          </div>
          <div className="confidence-bar">
            <div className="confidence-fill" style={{ width: `${selectedNode.metadata.confidence}%` }} />
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="inspector-tabs">
        {(['properties', 'transforms', 'history'] as const).map(tab => (
          <button key={tab} className={`inspector-tab ${activeTab === tab ? 'active' : ''}`}
            onClick={() => setActiveTab(tab)}>
            {t(`inspector.tab${tab.charAt(0).toUpperCase() + tab.slice(1)}` as any)}
          </button>
        ))}
      </div>

      <div className="inspector-content">
        {/* Properties tab */}
        {activeTab === 'properties' && (
          <div className="props-list fade-in">
            {selectedNode.metadata?.source && (
              <div className="prop-row">
                <span className="prop-key">{t('inspector.propSource')}</span>
                <span className="prop-val">{selectedNode.metadata.source}</span>
              </div>
            )}
            {selectedNode.metadata?.createdAt && (
              <div className="prop-row">
                <span className="prop-key"><Clock size={10} /> {t('inspector.propCreated')}</span>
                <span className="prop-val">{new Date(selectedNode.metadata.createdAt).toLocaleString()}</span>
              </div>
            )}
            {Object.entries(selectedNode.properties).map(([k, v]) => (
              <div key={k} className="prop-row">
                <span className="prop-key">{k}</span>
                <span className="prop-val prop-val-copy" onClick={() => navigator.clipboard.writeText(v)}>
                  {v} <Copy size={9} />
                </span>
              </div>
            ))}
            {selectedNode.metadata?.tags?.length && (
              <div className="prop-row">
                <span className="prop-key">{t('inspector.propTags')}</span>
                <div className="tag-list">
                  {selectedNode.metadata.tags.map(tag => (
                    <span key={tag} className="tag">{tag}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Transforms tab */}
        {activeTab === 'transforms' && (
          <TransformPanel node={selectedNode} />
        )}

        {/* History tab */}
        {activeTab === 'history' && (
          <div className="history-list fade-in">
            {(!selectedNode.transformHistory || selectedNode.transformHistory.length === 0) && (
              <div className="node-list-empty">{t('inspector.noHistory')}</div>
            )}
            {selectedNode.transformHistory?.map((entry, i) => (
              <div key={i} className={`history-item status-${entry.status}`}>
                <div className="history-transform">{entry.transformName}</div>
                <div className="history-meta">
                  <span>{t('inspector.historyResults', { count: entry.resultCount })}</span>
                  <span>{new Date(entry.ranAt).toLocaleTimeString()}</span>
                </div>
                {entry.error && <div className="history-error">{entry.error}</div>}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
