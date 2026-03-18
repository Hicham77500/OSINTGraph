import React, { useState, useEffect } from 'react'
import { Play, Loader, CheckCircle, XCircle, ChevronRight } from 'lucide-react'
import { NodeData } from '../../graph/nodeTypes'
import { useGraphStore } from '../../graph/graphStore'
import { apiClient } from '../../services/api'
import { wsClient } from '../../services/websocket'

interface Transform {
  name: string
  display_name: string
  input_type: string
  output_type: string
  description: string
}

interface ResultNode {
  type: string
  label: string
  properties?: Record<string, string>
}

interface TransformResult {
  nodes: ResultNode[]
  edges: Array<{ source: string; target: string; type: string }>
  log: string[]
}

interface TransformPanelProps {
  node: NodeData
}

export const TransformPanel: React.FC<TransformPanelProps> = ({ node }) => {
  const [transforms, setTransforms] = useState<Transform[]>([])
  const [running, setRunning] = useState<string | null>(null)
  const [logs, setLogs] = useState<string[]>([])
  const [results, setResults] = useState<TransformResult | null>(null)
  const { addNode, addEdge, updateNode } = useGraphStore()

  useEffect(() => {
    apiClient.get('/transforms').then(res => {
      if (res.ok && res.data) {
        const compatible = (res.data as Transform[]).filter(
          t => t.input_type === node.type || t.input_type === '*'
        )
        setTransforms(compatible)
      }
    }).catch(() => {
      // Fallback mock transforms
      setTransforms([
        { name: 'dns_lookup', display_name: 'DNS Lookup', input_type: 'domain', output_type: 'ip', description: 'Resolve domain to IPs' },
        { name: 'whois_lookup', display_name: 'Whois Lookup', input_type: 'domain', output_type: 'organization', description: 'Whois registration data' },
        { name: 'hibp_lookup', display_name: 'HaveIBeenPwned', input_type: 'email', output_type: 'breach', description: 'Check breach databases' },
        { name: 'shodan_lookup', display_name: 'Shodan Lookup', input_type: 'ip', output_type: 'service', description: 'Port & service discovery' },
      ].filter(t => t.input_type === node.type))
    })
  }, [node.type])

  const runTransform = async (transform: Transform) => {
    setRunning(transform.name)
    setLogs([`[${transform.display_name}] Starting...`])
    setResults(null)

    try {
      const res = await apiClient.post('/transforms/run', {
        transform: transform.name,
        input_type: node.type,
        value: node.label,
        node_id: node.id,
      })

      if (res.ok && res.data) {
        const data = res.data as TransformResult
        setResults(data)
        setLogs(prev => [...prev, ...(data.log ?? []), `✓ ${data.nodes.length} results found`])

        // Merge returned nodes/edges into graph
        const newNodes = data.nodes.map(n => {
          const store = useGraphStore.getState()
          return store.addNode(n.type as any, n.label, n.properties ?? {})
        })

        // Create edges from source node → new nodes
        newNodes.forEach(n => {
          useGraphStore.getState().addEdge(node.id, n.id, transform.output_type as any || 'linked_to')
        })

        // Update transform history
        updateNode(node.id, {
          transformHistory: [
            ...(node.transformHistory ?? []),
            {
              transformName: transform.display_name,
              ranAt: new Date().toISOString(),
              resultCount: data.nodes.length,
              status: 'success',
            }
          ]
        })
      }
    } catch (err: any) {
      setLogs(prev => [...prev, `✗ Error: ${err.message}`])
      updateNode(node.id, {
        transformHistory: [
          ...(node.transformHistory ?? []),
          {
            transformName: transform.display_name,
            ranAt: new Date().toISOString(),
            resultCount: 0,
            status: 'error',
            error: err.message,
          }
        ]
      })
    } finally {
      setRunning(null)
    }
  }

  return (
    <div className="transform-panel">
      {transforms.length === 0 && (
        <div className="node-list-empty" style={{ padding: '20px 16px' }}>
          No transforms available for <strong>{node.type}</strong>
        </div>
      )}

      <div className="transform-list">
        {transforms.map(t => (
          <div key={t.name} className="transform-item">
            <div className="transform-info">
              <div className="transform-name">{t.display_name}</div>
              <div className="transform-desc">{t.description}</div>
            </div>
            <button
              className={`btn btn-primary transform-run-btn ${running === t.name ? 'loading' : ''}`}
              onClick={() => runTransform(t)}
              disabled={running !== null}
            >
              {running === t.name
                ? <Loader size={12} className="loading-spin" />
                : <Play size={12} />
              }
              Run
            </button>
          </div>
        ))}
      </div>

      {/* Execution log */}
      {logs.length > 0 && (
        <div className="transform-log">
          {logs.map((l, i) => <div key={i} className="log-line">{l}</div>)}
        </div>
      )}
    </div>
  )
}
