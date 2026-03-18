import React, { useEffect, useRef, FC } from 'react'
import cytoscape from 'cytoscape'
// @ts-ignore
import cola from 'cytoscape-cola'
// @ts-ignore
import dagre from 'cytoscape-dagre'
import { useGraphStore } from './graphStore'
import { NODE_TYPE_CONFIG, NodeData, EdgeData } from './nodeTypes'
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
  // For pure icon rendering, we don't need color maps per type here anymore
  // since the SVG itself will be colored, and backgrounds are transparent.
  const typeStyles = Object.entries(NODE_TYPE_CONFIG).map(([type, cfg]) => ({
    selector: `node[type="${type}"]`,
    style: {} as any,
  }))

  return [
    // ── Nodes ──────────────────────────────────────────
    {
      selector: 'node',
      style: {
        shape: 'rectangle', // Shape doesn't matter visually due to 0 opacity
        width:  48,         // Icon size mapped precisely
        height: 48,
        'background-opacity': 0, // Transparent, Maltego-style standalone icons
        'border-width': 0,
        
        // Pure SVG icon
        'background-image':   'data(iconImage)',
        'background-fit':     'contain',

        // Label below the icon
        content:         'data(label)',
        'text-valign':   'bottom',
        'text-halign':   'center',
        'font-family':   'Inter, sans-serif',
        'font-size':     '11px',
        'font-weight':   '500',
        color:           '#e2e8f0',
        'text-margin-y':    6,
        'text-outline-width': 3,
        'text-outline-color': '#0a0c14',
        'text-max-width':   '110px',
        'text-wrap':        'ellipsis',
      } as any,
    },
    // Per-type colors
    ...typeStyles,
    // Selected (Maltego style glow around the icon)
    {
      selector: 'node:selected',
      style: {
        'underlay-color': '#6366f1',
        'underlay-padding': 6,
        'underlay-opacity': 0.3,
        'underlay-shape': 'ellipse',
      } as any,
    },
    {
      selector: 'node:active',
      style: { 'overlay-opacity': 0.08 } as any,
    },

    // ── Edges ──────────────────────────────────────────
    {
      selector: 'edge',
      style: {
        width: 1.5,
        'line-color':          'rgba(148,163,184,0.4)',
        'target-arrow-color':  'rgba(148,163,184,0.4)',
        'target-arrow-shape':  'triangle',
        'curve-style':         'bezier',
        label:                 'data(label)',
        'font-size':           '10px',
        'font-family':         'Inter, sans-serif',
        color:                 '#64748b',
        'text-outline-width':  2,
        'text-outline-color':  '#0a0c14',
      } as any,
    },
    {
      selector: 'edge:selected',
      style: {
        'line-color':         '#6366f1',
        'target-arrow-color': '#6366f1',
        width: 2.5,
      } as any,
    },
    {
      selector: '.faded',
      style: { opacity: 0.2 } as any,
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

  const { nodes, edges, layoutType, selectNode, selectEdge } = useGraphStore()

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

    cy.on('tap', 'node', e => selectNode(e.target.id()))
    cy.on('tap', 'edge', e => selectEdge(e.target.id()))
    cy.on('tap',         e => { if (e.target === cy) { selectNode(null); selectEdge(null) } })
    cy.on('cxttap',      e => {
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
      if (cy.getElementById(n.id).length === 0) {
        cy.add({
          group: 'nodes',
          data: {
            id:    n.id,
            label: n.label,
            type:  n.type,
            iconImage: getIconSvgUri(cfg.iconSvg, cfg.color), // Colored raw SVG string
          },
        })
      } else {
        // Update label if it changed
        cy.getElementById(n.id).data('label', n.label)
      }
    })

    // Add new edges
    edges.forEach((e: EdgeData) => {
      if (cy.getElementById(e.id).length === 0) {
        cy.add({
          group: 'edges',
          data: {
            id:     e.id,
            source: e.source,
            target: e.target,
            label:  e.label ?? e.type,
          },
        })
      }
    })

    // Re-run layout only when node count changes
    if (nodes.length > 0) {
      cy.layout(LAYOUT_OPTIONS[layoutType] ?? LAYOUT_OPTIONS.force).run()
    }
  }, [nodes, edges, layoutType])

  // ── Re-layout on layout-type switch ───────────────
  useEffect(() => {
    const cy = cyRef.current
    if (!cy || cy.nodes().length === 0) return
    cy.layout(LAYOUT_OPTIONS[layoutType] ?? LAYOUT_OPTIONS.force).run()
  }, [layoutType])

  return (
    <div className="graph-canvas-wrapper">
      <div ref={containerRef} className="graph-canvas" />
      {nodes.length === 0 && (
        <div className="graph-empty-state">
          <div className="graph-empty-icon">🕵️</div>
          <h2>Start your investigation</h2>
          <p>Add an entity from the left panel, or import a CSV / JSON file</p>
        </div>
      )}
    </div>
  )
}

export default GraphCanvas
