import React, { useState } from 'react'
import { GraphCanvas } from '../../graph/GraphCanvas'
import { Toolbar } from './Toolbar'
import { EntityPanel } from '../panels/EntityPanel'
import { InspectorPanel } from '../panels/InspectorPanel'
import { ContextMenu } from '../menus/ContextMenu'
import './MainLayout.css'

interface ContextMenuState {
  x: number
  y: number
  nodeId?: string
  edgeId?: string
}

export const MainLayout: React.FC = () => {
  const [contextMenu, setContextMenu] = useState<ContextMenuState | null>(null)
  const [leftCollapsed, setLeftCollapsed] = useState(false)
  const [rightCollapsed, setRightCollapsed] = useState(false)

  const handleContextMenu = (event: ContextMenuState) => {
    setContextMenu(event)
  }

  const closeContextMenu = () => setContextMenu(null)

  return (
    <div className="main-layout" onClick={closeContextMenu}>
      {/* Top toolbar */}
      <Toolbar
        leftCollapsed={leftCollapsed}
        rightCollapsed={rightCollapsed}
        onToggleLeft={() => setLeftCollapsed(v => !v)}
        onToggleRight={() => setRightCollapsed(v => !v)}
      />

      <div className="main-body">
        {/* Left sidebar — Entity types */}
        <aside className={`sidebar sidebar-left ${leftCollapsed ? 'collapsed' : ''}`}>
          <EntityPanel />
        </aside>

        {/* Central canvas */}
        <main className="canvas-area">
          <GraphCanvas onContextMenu={handleContextMenu} />
        </main>

        {/* Right sidebar — Inspector */}
        <aside className={`sidebar sidebar-right ${rightCollapsed ? 'collapsed' : ''}`}>
          <InspectorPanel />
        </aside>
      </div>

      {/* Context menu */}
      {contextMenu && (
        <ContextMenu
          x={contextMenu.x}
          y={contextMenu.y}
          nodeId={contextMenu.nodeId}
          edgeId={contextMenu.edgeId}
          onClose={closeContextMenu}
        />
      )}
    </div>
  )
}
