import React, { useEffect, useRef } from 'react'
import { Expand, Trash2, Copy, Scissors, Link, Zap, ChevronRight } from 'lucide-react'
import { useGraphStore } from '../../graph/graphStore'
import { ALL_EDGE_TYPES, EDGE_TYPE_CONFIG } from '../../graph/nodeTypes'
import './ContextMenu.css'

interface ContextMenuProps {
  x: number
  y: number
  nodeId?: string
  edgeId?: string
  onClose: () => void
}

export const ContextMenu: React.FC<ContextMenuProps> = ({ x, y, nodeId, edgeId, onClose }) => {
  const ref = useRef<HTMLDivElement>(null)
  const { nodes, removeNode, removeEdge, selectNode } = useGraphStore()
  const node = nodes.find(n => n.id === nodeId)

  // Clamp to viewport
  useEffect(() => {
    if (!ref.current) return
    const rect = ref.current.getBoundingClientRect()
    const el = ref.current
    if (rect.right > window.innerWidth) el.style.left = `${x - rect.width}px`
    if (rect.bottom > window.innerHeight) el.style.top = `${y - rect.height}px`
  }, [x, y])

  const handleExpand = () => {
    if (nodeId) selectNode(nodeId)
    onClose()
  }

  const handleDelete = () => {
    if (nodeId) removeNode(nodeId)
    if (edgeId) removeEdge(edgeId)
    onClose()
  }

  const handleCopy = () => {
    if (node) navigator.clipboard.writeText(node.label)
    onClose()
  }

  return (
    <div
      ref={ref}
      className="context-menu fade-in"
      style={{ left: x, top: y }}
      onClick={e => e.stopPropagation()}
    >
      {nodeId && node && (
        <>
          <div className="context-header">
            <span className="context-node-label">{node.label}</span>
            <span className="context-node-type">{node.type}</span>
          </div>
          <div className="context-divider" />

          <button className="context-item" onClick={handleExpand}>
            <Expand size={13} /> Inspect node
          </button>
          <button className="context-item" onClick={handleCopy}>
            <Copy size={13} /> Copy value
          </button>

          <div className="context-divider" />

          <button className="context-item context-item-danger" onClick={handleDelete}>
            <Trash2 size={13} /> Delete node
          </button>
        </>
      )}

      {edgeId && !nodeId && (
        <>
          <div className="context-header">
            <span className="context-node-label">Edge</span>
          </div>
          <button className="context-item context-item-danger" onClick={handleDelete}>
            <Trash2 size={13} /> Delete edge
          </button>
        </>
      )}

      {!nodeId && !edgeId && (
        <>
          <div className="context-header">
            <span className="context-node-label">Canvas</span>
          </div>
          <button className="context-item" onClick={onClose}>
            <Zap size={13} /> New investigation
          </button>
        </>
      )}
    </div>
  )
}
