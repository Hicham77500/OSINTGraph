import React, { useState } from 'react'
import { ALL_NODE_TYPES, NODE_TYPE_CONFIG, NodeType, createNode } from '../../graph/nodeTypes'
import { useGraphStore } from '../../graph/graphStore'
import { Plus, Search, ChevronDown } from 'lucide-react'
import './EntityPanel.css'

export const EntityPanel: React.FC = () => {
  const { addNode, nodes } = useGraphStore()
  const [search, setSearch] = useState('')
  const [addingType, setAddingType] = useState<NodeType | null>(null)
  const [newLabel, setNewLabel] = useState('')

  const filteredNodes = nodes.filter(n =>
    n.label.toLowerCase().includes(search.toLowerCase()) ||
    n.type.toLowerCase().includes(search.toLowerCase())
  )

  const handleAdd = (type: NodeType) => {
    if (addingType === type) {
      if (newLabel.trim()) {
        addNode(type, newLabel.trim())
        setNewLabel('')
      }
      setAddingType(null)
    } else {
      setAddingType(type)
      setNewLabel('')
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent, type: NodeType) => {
    if (e.key === 'Enter') handleAdd(type)
    if (e.key === 'Escape') { setAddingType(null); setNewLabel('') }
  }

  // Count per type
  const countByType = (type: NodeType) => nodes.filter(n => n.type === type).length

  return (
    <div className="entity-panel">
      <div className="panel-header">
        <h3>Entities</h3>
        <span className="panel-badge">{nodes.length}</span>
      </div>

      {/* Entity type palette */}
      <div className="entity-types-section">
        <div className="section-label">Types</div>
        <div className="entity-type-list">
          {ALL_NODE_TYPES.map(type => {
            const cfg = NODE_TYPE_CONFIG[type]
            const isAdding = addingType === type
            return (
              <div key={type} className={`entity-type-item ${isAdding ? 'adding' : ''}`}
                style={{ '--entity-color': cfg.color } as React.CSSProperties}>
                <div className="entity-type-row">
                  <div className="entity-icon" style={{ background: 'transparent' }}>
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="22" height="22" fill="none" stroke={cfg.color} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" dangerouslySetInnerHTML={{ __html: cfg.iconSvg }} />
                  </div>
                  <div className="entity-info">
                    <span className="entity-label">{cfg.label}</span>
                    <span className="entity-count">{countByType(type)}</span>
                  </div>
                  <button className="entity-add-btn" onClick={() => handleAdd(type)}
                    title={`Add ${cfg.label}`}>
                    <Plus size={12} />
                  </button>
                </div>
                {isAdding && (
                  <div className="entity-add-input fade-in">
                    <input
                      autoFocus
                      type="text"
                      placeholder={`Enter ${cfg.label.toLowerCase()} value…`}
                      value={newLabel}
                      onChange={e => setNewLabel(e.target.value)}
                      onKeyDown={e => handleKeyDown(e, type)}
                    />
                    <button className="btn btn-primary" style={{ padding: '4px 10px', fontSize: 11 }}
                      onClick={() => handleAdd(type)}>Add</button>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>

      <div className="divider" />

      {/* Node list */}
      <div className="entity-list-section">
        <div className="section-label">In graph</div>
        <div className="entity-search">
          <Search size={11} className="search-icon" />
          <input type="text" placeholder="Filter…" value={search}
            onChange={e => setSearch(e.target.value)} />
        </div>
        <div className="node-list">
          {filteredNodes.length === 0 && (
            <div className="node-list-empty">No nodes yet</div>
          )}
          {filteredNodes.map(n => {
            const cfg = NODE_TYPE_CONFIG[n.type]
            const { selectNode, selectedNodeId } = useGraphStore.getState()
            return (
              <button key={n.id}
                className={`node-list-item ${selectedNodeId === n.id ? 'selected' : ''}`}
                onClick={() => selectNode(n.id)}>
                <span className="node-list-icon" style={{ color: cfg.color, display: 'flex' }}>
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" dangerouslySetInnerHTML={{ __html: cfg.iconSvg }} />
                </span>
                <span className="node-list-label">{n.label}</span>
                <span className="node-list-type">{cfg.label}</span>
              </button>
            )
          })}
        </div>
      </div>
    </div>
  )
}
