import React, { useEffect, useRef, useState, FC } from 'react'
import cytoscape from 'cytoscape'
import { useTranslation } from 'react-i18next'
// @ts-ignore
import cola from 'cytoscape-cola'
// @ts-ignore
import dagre from 'cytoscape-dagre'
import { useGraphStore } from './graphStore'
import { NODE_TYPE_CONFIG, EDGE_TYPE_CONFIG, NodeData, EdgeData, EdgeType } from './nodeTypes'
import './GraphCanvas.css'

cytoscape.use(cola)
cytoscape.use(dagre)

interface GraphCanvasProps {
  onContextMenu?: (event: { x: number; y: number; nodeId?: string; edgeId?: string }) => void
}

/** Render an SVG icon to a base64 Data URL for Cytoscape */
function getIconSvgUri(svgPath: string, color: string): string {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="${color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">${svgPath}</svg>`
  try {
    return 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svg)))
  } catch {
    return ''
  }
}


// -------------------------------------------------------
// Cytoscape stylesheet
// -------------------------------------------------------
function buildCytoscapeStyle(): cytoscape.StylesheetStyle[] {
  return [
    // ── Nodes ──────────────────────────────────────────
    {
      selector: 'node',
      style: {
        shape: 'ellipse',
        width:  64,
        height: 64,

        // Colored bubble (entity-type color via data attribute)
        'background-color':   'data(bgColor)',
        'background-opacity': 0.13,
        'border-width':       1.5,
        'border-color':       'data(bgColor)',
        'border-opacity':     0.45,

        // Icon centered inside the bubble
        'background-image':    'data(iconImage)',
        'background-width':    '62%',
        'background-height':   '62%',
        'background-position-x': '50%',
        'background-position-y': '50%',

        // Label below the node
        content:              'data(label)',
        'text-valign':        'bottom',
        'text-halign':        'center',
        'font-family':        'Inter, sans-serif',
        'font-size':          '11px',
        'font-weight':        '500',
        color:                '#e2e8f0',
        'text-margin-y':      8,
        'text-outline-width': 3,
        'text-outline-color': '#0a0c14',
        'text-max-width':     '110px',
        'text-wrap':          'ellipsis',
      } as any,
    },
    // Selected: brighter ring + glow
    {
      selector: 'node:selected',
      style: {
        'background-opacity': 0.28,
        'border-width':       2.5,
        'border-opacity':     0.9,
        'underlay-color':     'data(bgColor)',
        'underlay-padding':   10,
        'underlay-opacity':   0.18,
        'underlay-shape':     'ellipse',
      } as any,
    },
    {
      selector: 'node:active',
      style: { 'overlay-opacity': 0.07 } as any,
    },

    // ── Edges ──────────────────────────────────────────
    {
      selector: 'edge',
      style: {
        width:                 1.8,
        'line-color':          'data(edgeColor)',
        'target-arrow-color':  'data(edgeColor)',
        'target-arrow-shape':  'triangle',
        'arrow-scale':         0.9,
        'curve-style':         'bezier',
        label:                 'data(label)',
        'font-size':           '10px',
        'font-family':         'Inter, sans-serif',
        color:                 '#94a3b8',
        'text-outline-width':  2,
        'text-outline-color':  '#0a0c14',
        'text-background-opacity': 0,
      } as any,
    },
    {
      selector: 'edge:selected',
      style: {
        'line-color':         '#6366f1',
        'target-arrow-color': '#6366f1',
        width: 2.8,
      } as any,
    },
    // ── Connect-mode highlight ──────────────────────
    {
      selector: 'node.connect-source',
      style: {
        'background-opacity': 0.5,
        'border-width':       3,
        'border-opacity':     1,
        'underlay-color':     'data(bgColor)',
        'underlay-padding':   14,
        'underlay-opacity':   0.30,
        'underlay-shape':     'ellipse',
      } as any,
    },
  ]
}

// -------------------------------------------------------
// Layout presets
// -------------------------------------------------------
const LAYOUT_OPTIONS: Record<string, any> = {
  force: {
    name: 'cola',
    animate: true,
    randomize: false,
    nodeSpacing: 70,
    maxSimulationTime: 3000,
    fit: true,
    padding: 60,
  },
  hierarchical: {
    name: 'dagre',
    rankDir: 'TB',
    animate: true,
    padding: 60,
    fit: true,
    spacingFactor: 1.5,
  },
  grid: {
    name: 'grid',
    animate: true,
    padding: 60,
    fit: true,
  },
}

// -------------------------------------------------------
// Component
// -------------------------------------------------------
export const GraphCanvas: FC<GraphCanvasProps> = ({ onContextMenu }) => {
  const containerRef = useRef<HTMLDivElement>(null)
  const cyRef        = useRef<cytoscape.Core | null>(null)
  const prevNodeCountRef = useRef(0)
  const { t, i18n } = useTranslation()

  // Connect mode local state
  const [pendingSource, setPendingSource] = useState<string | null>(null)
  const [pendingTarget, setPendingTarget] = useState<string | null>(null)

  const {
    nodes, edges, layoutType, selectNode, selectEdge,
    connectMode, setConnectMode, addEdge,
  } = useGraphStore()

  // Cancel connect mode with Escape key
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && connectMode) {
        setConnectMode(false)
        setPendingSource(null)
        setPendingTarget(null)
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [connectMode, setConnectMode])

  // ── Init Cytoscape once ────────────────────────────
  useEffect(() => {
    if (!containerRef.current) return

    const cy = cytoscape({
      container:          containerRef.current,
      style:              buildCytoscapeStyle(),
      layout:             { name: 'preset' },
      wheelSensitivity:   1.0, // Increased mouse wheel zooming speed (default was very slow)
      minZoom:            0.05,
      maxZoom:            5,
      userPanningEnabled: true,
      userZoomingEnabled: true,
      boxSelectionEnabled: true,
      autounselectify:    false,
    })

    cyRef.current = cy

    // Use refs to avoid stale closures in Cytoscape event handlers
    const connectModeRef   = { current: false }
    const pendingSourceRef = { current: null as string | null }

    // Expose mutable refs so the effect below can update them
    ;(cy as any)._connectModeRef   = connectModeRef
    ;(cy as any)._pendingSourceRef = pendingSourceRef

    cy.on('tap', 'node', e => {
      const nodeId = e.target.id()
      if (connectModeRef.current) {
        if (!pendingSourceRef.current) {
          // First click: set source
          pendingSourceRef.current = nodeId
          setPendingSource(nodeId)
        } else if (pendingSourceRef.current !== nodeId) {
          // Second click: set target, show type picker
          setPendingTarget(nodeId)
        }
        return
      }
      selectNode(nodeId)
    })
    cy.on('tap', 'edge', e => { if (!connectModeRef.current) selectEdge(e.target.id()) })
    cy.on('tap', e => {
      if (e.target === cy) {
        if (connectModeRef.current) {
          // Click on canvas cancels pending source
          pendingSourceRef.current = null
          setPendingSource(null)
          setPendingTarget(null)
        } else {
          selectNode(null)
          selectEdge(null)
        }
      }
    })
    cy.on('cxttap', e => {
      const isNode = e.target !== cy && e.target.isNode?.()
      const isEdge = e.target !== cy && e.target.isEdge?.()
      onContextMenu?.({
        x:      (e.originalEvent as MouseEvent).clientX,
        y:      (e.originalEvent as MouseEvent).clientY,
        nodeId: isNode ? e.target.id() : undefined,
        edgeId: isEdge ? e.target.id() : undefined,
      })
    })

    return () => cy.destroy()
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  // ── Sync connect mode into Cytoscape refs ─────────
  useEffect(() => {
    const cy = cyRef.current
    if (!cy) return
    const cmRef = (cy as any)._connectModeRef
    const psRef = (cy as any)._pendingSourceRef
    if (cmRef) cmRef.current = connectMode
    if (psRef) psRef.current = pendingSource

    // Highlight pending source node
    cy.nodes().removeClass('connect-source connect-target')
    if (pendingSource) {
      cy.getElementById(pendingSource).addClass('connect-source')
    }
  }, [connectMode, pendingSource])

  // ── Sync store → Cytoscape ────────────────────────
  useEffect(() => {
    const cy = cyRef.current
    if (!cy) return

    const nodeIds = new Set(nodes.map((n: NodeData) => n.id))
    const edgeIds = new Set(edges.map((e: EdgeData) => e.id))

    // Remove stale elements
    cy.nodes().forEach(n => { if (!nodeIds.has(n.id())) n.remove() })
    cy.edges().forEach(e => { if (!edgeIds.has(e.id())) e.remove() })

    // Add / update nodes
    nodes.forEach((n: NodeData) => {
      const cfg = NODE_TYPE_CONFIG[n.type]
      const iconImage = getIconSvgUri(cfg.iconSvg, cfg.color)
      if (cy.getElementById(n.id).length === 0) {
        cy.add({
          group: 'nodes',
          data: {
            id:        n.id,
            label:     n.label,
            type:      n.type,
            iconImage,
            bgColor:   cfg.color,
          },
        })
      } else {
        // Update label, type, icon and color on change
        const el = cy.getElementById(n.id)
        el.data('label',     n.label)
        el.data('type',      n.type)
        el.data('iconImage', iconImage)
        el.data('bgColor',   cfg.color)
      }
    })

    // Add / update edges
    edges.forEach((e: EdgeData) => {
      const edgeCfg = EDGE_TYPE_CONFIG[e.type as EdgeType]
      const translatedLabel = t(`edgeTypes.${e.type}` as any, { defaultValue: edgeCfg?.label ?? e.type })
      if (cy.getElementById(e.id).length === 0) {
        cy.add({
          group: 'edges',
          data: {
            id:        e.id,
            source:    e.source,
            target:    e.target,
            label:     translatedLabel,
            edgeColor: edgeCfg ? `${edgeCfg.color}99` : 'rgba(148,163,184,0.5)',
          },
        })
      } else {
        // Update label when language changes
        cy.getElementById(e.id).data('label', translatedLabel)
      }
    })

    // Re-run layout only when the number of nodes changes (not on metadata updates)
    const nodeCountChanged = nodes.length !== prevNodeCountRef.current
    prevNodeCountRef.current = nodes.length
    if (nodes.length > 0 && nodeCountChanged) {
      cy.layout(LAYOUT_OPTIONS[layoutType] ?? LAYOUT_OPTIONS.force).run()
    }
  }, [nodes, edges, layoutType, i18n.language])

  // ── Re-layout on layout-type switch ───────────────
  useEffect(() => {
    const cy = cyRef.current
    if (!cy || cy.nodes().length === 0) return
    cy.layout(LAYOUT_OPTIONS[layoutType] ?? LAYOUT_OPTIONS.force).run()
  }, [layoutType])

  const handleEdgeTypePick = (type: EdgeType) => {
    if (pendingSource && pendingTarget) {
      addEdge(pendingSource, pendingTarget, type)
    }
    setPendingSource(null)
    setPendingTarget(null)
    // Keep connect mode active for chaining
    // (cy refs will be updated by the sync effect)
    const cy = cyRef.current
    if (cy) {
      const cmRef = (cy as any)._connectModeRef
      const psRef = (cy as any)._pendingSourceRef
      if (cmRef) cmRef.current = connectMode
      if (psRef) psRef.current = null
      cy.nodes().removeClass('connect-source')
    }
  }

  const cancelConnect = () => {
    setPendingSource(null)
    setPendingTarget(null)
    setConnectMode(false)
  }

  return (
    <div className={`graph-canvas-wrapper${connectMode ? ' connecting-mode' : ''}`}>
      <div ref={containerRef} className="graph-canvas" />

      {/* Connect mode hint banner */}
      {connectMode && !pendingTarget && (
        <div className="connect-hint">
          {pendingSource
            ? t('canvas.connectPickTarget')
            : t('canvas.connectPickSource')}
          <button className="connect-hint-cancel" onClick={cancelConnect}>✕ {t('canvas.connectCancel')}</button>
        </div>
      )}

      {/* Edge type picker — shown when source + target are both selected */}
      {pendingSource && pendingTarget && (
        <div className="edge-type-picker-overlay" onClick={e => e.stopPropagation()}>
          <div className="edge-type-picker">
            <div className="etp-title">{t('canvas.connectChooseType')}</div>
            {(Object.entries(EDGE_TYPE_CONFIG) as [EdgeType, {color: string; label: string}][]).map(([type, cfg]) => (
              <button
                key={type}
                className="etp-option"
                style={{ '--edge-color': cfg.color } as React.CSSProperties}
                onClick={() => handleEdgeTypePick(type)}
              >
                <span className="etp-dot" />
                <span className="etp-label">{t(`edgeTypes.${type}` as any, { defaultValue: cfg.label })}</span>
              </button>
            ))}
            <button className="etp-cancel" onClick={() => { setPendingSource(null); setPendingTarget(null) }}>
              {t('canvas.connectCancel')}
            </button>
          </div>
        </div>
      )}

      {nodes.length === 0 && (
        <div className="graph-empty-state">
          <div className="graph-empty-icon">🕵️</div>
          <h2>{t('canvas.emptyTitle')}</h2>
          <p>{t('canvas.emptyDesc')}</p>
        </div>
      )}
    </div>
  )
}

export default GraphCanvas
