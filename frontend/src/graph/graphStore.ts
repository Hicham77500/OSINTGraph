import { create } from 'zustand'
import { NodeData, EdgeData, createNode, createEdge, NodeType, EdgeType } from './nodeTypes'

export interface HistoryEntry {
  nodes: NodeData[]
  edges: EdgeData[]
  description: string
}

export interface GraphState {
  // Data
  nodes: NodeData[]
  edges: EdgeData[]
  selectedNodeId: string | null
  selectedEdgeId: string | null

  // Workspaces
  currentWorkspace: string
  workspaces: string[]

  // History
  history: HistoryEntry[]
  historyIndex: number

  // UI state
  isLoading: boolean
  layoutType: 'force' | 'hierarchical' | 'grid'
  connectMode: boolean

  // Actions
  addNode: (type: NodeType, label: string, properties?: Record<string, string>) => NodeData
  addEdge: (source: string, target: string, type: EdgeType) => EdgeData
  updateNode: (id: string, data: Partial<NodeData>) => void
  removeNode: (id: string) => void
  removeEdge: (id: string) => void
  selectNode: (id: string | null) => void
  selectEdge: (id: string | null) => void
  mergeNodes: (incoming: NodeData[], incomingEdges?: EdgeData[]) => void

  // History
  undo: () => void
  redo: () => void
  _pushHistory: (description: string) => void

  // Persistence
  loadGraph: (nodes: NodeData[], edges: EdgeData[]) => void
  clearGraph: () => void
  setWorkspace: (name: string) => void
  setLayout: (layout: 'force' | 'hierarchical' | 'grid') => void
  setConnectMode: (v: boolean) => void
}

export const useGraphStore = create<GraphState>((set, get) => ({
  nodes: [],
  edges: [],
  selectedNodeId: null,
  selectedEdgeId: null,
  currentWorkspace: 'default',
  workspaces: ['default'],
  history: [{ nodes: [], edges: [], description: 'initial' }],
  historyIndex: 0,
  isLoading: false,
  layoutType: 'force',
  connectMode: false,

  addNode: (type, label, properties = {}) => {
    const node = createNode(type, label, properties)
    set(s => ({ nodes: [...s.nodes, node] }))
    get()._pushHistory(`Add ${type}: ${label}`)
    return node
  },

  addEdge: (source, target, type) => {
    const edge = createEdge(source, target, type)
    set(s => ({ edges: [...s.edges, edge] }))
    get()._pushHistory(`Add relation: ${type}`)
    return edge
  },

  updateNode: (id, data) => {
    set(s => ({
      nodes: s.nodes.map(n => n.id === id ? { ...n, ...data } : n)
    }))
  },

  removeNode: (id) => {
    set(s => ({
      nodes: s.nodes.filter(n => n.id !== id),
      edges: s.edges.filter(e => e.source !== id && e.target !== id),
      selectedNodeId: s.selectedNodeId === id ? null : s.selectedNodeId,
    }))
    get()._pushHistory('Remove node')
  },

  removeEdge: (id) => {
    set(s => ({ edges: s.edges.filter(e => e.id !== id) }))
    get()._pushHistory('Remove edge')
  },

  selectNode: (id) => set({ selectedNodeId: id, selectedEdgeId: null }),
  selectEdge: (id) => set({ selectedEdgeId: id, selectedNodeId: null }),

  mergeNodes: (incoming, incomingEdges = []) => {
    set(s => {
      const existingIds = new Set(s.nodes.map(n => n.id))
      const existingEdgeIds = new Set(s.edges.map(e => e.id))
      const newNodes = incoming.filter(n => !existingIds.has(n.id))
      const newEdges = incomingEdges.filter(e => !existingEdgeIds.has(e.id))
      return {
        nodes: [...s.nodes, ...newNodes],
        edges: [...s.edges, ...newEdges],
      }
    })
    get()._pushHistory(`Merge ${incoming.length} nodes`)
  },

  _pushHistory: (description) => {
    const { nodes, edges, history, historyIndex } = get()
    const snapshot: HistoryEntry = {
      nodes: JSON.parse(JSON.stringify(nodes)),
      edges: JSON.parse(JSON.stringify(edges)),
      description,
    }
    const trimmed = history.slice(0, historyIndex + 1)
    set({
      history: [...trimmed, snapshot].slice(-50), // keep last 50
      historyIndex: Math.min(trimmed.length, 49),
    })
  },

  undo: () => {
    const { historyIndex, history } = get()
    if (historyIndex <= 0) return
    const idx = historyIndex - 1
    const entry = history[idx]
    set({
      nodes: JSON.parse(JSON.stringify(entry.nodes)),
      edges: JSON.parse(JSON.stringify(entry.edges)),
      historyIndex: idx,
    })
  },

  redo: () => {
    const { historyIndex, history } = get()
    if (historyIndex >= history.length - 1) return
    const idx = historyIndex + 1
    const entry = history[idx]
    set({
      nodes: JSON.parse(JSON.stringify(entry.nodes)),
      edges: JSON.parse(JSON.stringify(entry.edges)),
      historyIndex: idx,
    })
  },

  loadGraph: (nodes, edges) => {
    set({
      nodes,
      edges,
      selectedNodeId: null,
      selectedEdgeId: null,
      history: [{ nodes: JSON.parse(JSON.stringify(nodes)), edges: JSON.parse(JSON.stringify(edges)), description: 'loaded' }],
      historyIndex: 0,
    })
  },

  clearGraph: () => {
    set({ nodes: [], edges: [], selectedNodeId: null, selectedEdgeId: null })
    get()._pushHistory('Clear graph')
  },

  setWorkspace: (name) => set({ currentWorkspace: name }),
  setLayout: (layout) => set({ layoutType: layout }),
  setConnectMode: (v) => set({ connectMode: v }),
}))
