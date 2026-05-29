// ============================================================
// Node Types — OsintGraph Entity System
// ============================================================

export type NodeType = 
  | 'person'
  | 'email'
  | 'domain'
  | 'ip'
  | 'username'
  | 'organization'

export type EdgeType = 
  | 'owns'
  | 'linked_to'
  | 'resolves_to'
  | 'uses'

export interface NodeData {
  id: string
  type: NodeType
  label: string
  properties: Record<string, string>
  metadata?: {
    source?: string
    confidence?: number
    createdAt?: string
    updatedAt?: string
    tags?: string[]
  }
  transformHistory?: TransformHistoryEntry[]
  notes?: string
}

export interface EdgeData {
  id: string
  source: string
  target: string
  type: EdgeType
  label?: string
  properties?: Record<string, string>
  createdAt?: string
}

export interface TransformHistoryEntry {
  transformName: string
  ranAt: string
  resultCount: number
  status: 'success' | 'error' | 'running'
  error?: string
}

// ---- Visual config per entity type ----

export interface NodeTypeConfig {
  color: string
  bgColor: string
  borderColor: string
  iconSvg: string    // Raw SVG inner content replacing emojis
  label: string
  description: string
}

export const NODE_TYPE_CONFIG: Record<NodeType, NodeTypeConfig> = {
  person: {
    color: '#6366f1',
    bgColor: 'rgba(99,102,241,0.15)',
    borderColor: 'rgba(99,102,241,0.6)',
    iconSvg: '<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
    label: 'Person',
    description: 'A real or suspected individual identity',
  },
  email: {
    color: '#22c55e',
    bgColor: 'rgba(34,197,94,0.15)',
    borderColor: 'rgba(34,197,94,0.6)',
    iconSvg: '<rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>',
    label: 'Email',
    description: 'An email address',
  },
  domain: {
    color: '#f59e0b',
    bgColor: 'rgba(245,158,11,0.15)',
    borderColor: 'rgba(245,158,11,0.6)',
    iconSvg: '<circle cx="12" cy="12" r="10"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/><path d="M2 12h20"/>',
    label: 'Domain',
    description: 'A domain name or subdomain',
  },
  ip: {
    color: '#ef4444',
    bgColor: 'rgba(239,68,68,0.15)',
    borderColor: 'rgba(239,68,68,0.6)',
    // Network topology: hub node (top) linked to two endpoint nodes (bottom)
    iconSvg: '<rect x="9" y="2" width="6" height="6" rx="1"/><rect x="2" y="16" width="6" height="6" rx="1"/><rect x="16" y="16" width="6" height="6" rx="1"/><path d="M5.69 16.25 12 8m6.31 8.25L12 8"/>',
    label: 'IP Address',
    description: 'IPv4 or IPv6 address',
  },
  username: {
    color: '#8b5cf6',
    bgColor: 'rgba(139,92,246,0.15)',
    borderColor: 'rgba(139,92,246,0.6)',
    iconSvg: '<circle cx="12" cy="12" r="4"/><path d="M16 8v5a3 3 0 0 0 6 0v-1a10 10 0 1 0-4 8"/>',
    label: 'Username',
    description: 'A username or handle on a platform',
  },
  organization: {
    color: '#38bdf8',
    bgColor: 'rgba(56,189,248,0.15)',
    borderColor: 'rgba(56,189,248,0.6)',
    // Building2: main tower + two wings + horizontal window lines (reads well at any size)
    iconSvg: '<path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z"/><path d="M6 12H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2"/><path d="M18 9h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2"/><path d="M10 6h4"/><path d="M10 10h4"/><path d="M10 14h4"/><path d="M10 18h4"/>',
    label: 'Organization',
    description: 'A company, group, or institution',
  },
}

export const EDGE_TYPE_CONFIG: Record<EdgeType, { color: string; label: string }> = {
  owns: { color: '#6366f1', label: 'Owns' },
  linked_to: { color: '#94a3b8', label: 'Linked To' },
  resolves_to: { color: '#f59e0b', label: 'Resolves To' },
  uses: { color: '#22c55e', label: 'Uses' },
}

export const ALL_NODE_TYPES: NodeType[] = ['person', 'email', 'domain', 'ip', 'username', 'organization']
export const ALL_EDGE_TYPES: EdgeType[] = ['owns', 'linked_to', 'resolves_to', 'uses']

// ---- Factory ----

let _idCounter = 0
export function generateId(prefix: string = 'node'): string {
  return `${prefix}_${Date.now()}_${++_idCounter}`
}

export function createNode(type: NodeType, label: string, properties: Record<string, string> = {}): NodeData {
  return {
    id: generateId(type),
    type,
    label,
    properties,
    metadata: {
      createdAt: new Date().toISOString(),
      confidence: 100,
      source: 'manual',
    },
    transformHistory: [],
  }
}

export function createEdge(source: string, target: string, type: EdgeType): EdgeData {
  return {
    id: generateId('edge'),
    source,
    target,
    type,
    label: EDGE_TYPE_CONFIG[type].label,
    createdAt: new Date().toISOString(),
  }
}
