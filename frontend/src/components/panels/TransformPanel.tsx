import React, { useState, useEffect } from 'react'
import { Play, Loader } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import {
  NodeData, EdgeData, EdgeType, NodeType,
  ALL_EDGE_TYPES, createNode, createEdge,
} from '../../graph/nodeTypes'
import { useGraphStore } from '../../graph/graphStore'
import { apiClient } from '../../services/api'

/** Maps a transform name to the most semantically accurate EdgeType */
const TRANSFORM_EDGE_TYPE: Record<string, EdgeType> = {
  dns_lookup:    'resolves_to',
  whois_lookup:  'owns',
  hibp_lookup:   'linked_to',
  shodan_lookup: 'linked_to',
}

function resolveEdgeType(transformName: string, outputType: string): EdgeType {
  if (TRANSFORM_EDGE_TYPE[transformName]) return TRANSFORM_EDGE_TYPE[transformName]
  if (ALL_EDGE_TYPES.includes(outputType as EdgeType)) return outputType as EdgeType
  return 'linked_to'
}

interface Transform {
  id: string
  name: string
  description: string
  category: string
  input_types: string[]
  output_types: string[]
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
  const { t } = useTranslation()

  useEffect(() => {
    apiClient.get('/transforms').then(res => {
      if (res.ok && res.data) {
        const compatible = (res.data as Transform[]).filter(
          t => t.input_types && (t.input_types.includes('*') || t.input_types.some(type => type.toLowerCase() === node.type.toLowerCase()))
        )
        setTransforms(compatible)
      }
    }).catch((err) => {
      console.error(err)
      setTransforms([])
    })
  }, [node.type])

  const runTransform = async (transform: Transform) => {
    setRunning(transform.id)
    setLogs([t('transforms.starting', { name: transform.name })])
    setResults(null)

    try {
      const res = await apiClient.post('/transforms/run', {
        transform: transform.id,
        input_type: node.type,
        value: node.label,
        node_id: node.id,
      })

      if (res.ok && res.data) {
        const data = res.data as TransformResult
        setResults(data)
        setLogs(prev => [...prev, ...(data.log ?? []), t('transforms.done', { count: data.nodes.length })])

        // Build node + edge objects, then merge atomically (single history entry)
        const edgeType = resolveEdgeType(transform.id, transform.output_types[0]?.toLowerCase() || 'linked_to')
        const newNodeObjects: NodeData[] = data.nodes.map(n =>
          createNode(n.type.toLowerCase() as NodeType, n.label, n.properties ?? {})
        )
        const newEdgeObjects: EdgeData[] = newNodeObjects.map(n =>
          createEdge(node.id, n.id, edgeType)
        )
        useGraphStore.getState().mergeNodes(newNodeObjects, newEdgeObjects)

        // Update transform history on the source node
        updateNode(node.id, {
          transformHistory: [
            ...(node.transformHistory ?? []),
            {
              transformName: transform.name,
              ranAt: new Date().toISOString(),
              resultCount: data.nodes.length,
              status: 'success',
            },
          ],
        })
      }
    } catch (err: any) {
      setLogs(prev => [...prev, t('transforms.error', { message: err.message })])
      updateNode(node.id, {
        transformHistory: [
          ...(node.transformHistory ?? []),
          {
            transformName: transform.name,
            ranAt: new Date().toISOString(),
            resultCount: 0,
            status: 'error',
            error: err.message,
          },
        ],
      })
    } finally {
      setRunning(null)
    }
  }

  return (
    <div className="transform-panel">
      {transforms.length === 0 && (
        <div className="node-list-empty" style={{ padding: '20px 16px' }}>
          {t('transforms.noTransforms', { type: node.type })}
        </div>
      )}

      <div className="transform-list">
        {transforms.map(tf => (
          <div key={tf.id} className="transform-item">
            <div className="transform-info">
              <div className="transform-name">{tf.name}</div>
              <div className="transform-desc">{tf.description}</div>
            </div>
            <button
              className={`btn btn-primary transform-run-btn ${running === tf.id ? 'loading' : ''}`}
              onClick={() => runTransform(tf)}
              disabled={running !== null}
            >
              {running === tf.id
                ? <Loader size={12} className="loading-spin" />
                : <Play size={12} />
              }
              {t('transforms.run')}
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
