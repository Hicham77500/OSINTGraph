import React, { useState, useEffect, useRef, useCallback } from 'react'
import { Play, Loader } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import {
  NodeData, EdgeData, EdgeType, NodeType,
  ALL_EDGE_TYPES, ALL_NODE_TYPES, createNode, createEdge,
} from '../../graph/nodeTypes'
import { useGraphStore } from '../../graph/graphStore'
import { apiClient } from '../../services/api'
import { ApiKeyHelp, type ApiKeyHelpItem } from '../common/ApiKeyHelp'
import { getSocket, wsClient } from '../../services/websocket'
import './TransformPanel.css'

/** Maps a transform name to the most semantically accurate EdgeType */
const TRANSFORM_EDGE_TYPE: Record<string, EdgeType> = {
  dns_lookup:       'resolves_to',
  whois_lookup:     'owns',
  hibp_lookup:      'linked_to',
  shodan_lookup:    'linked_to',
  holehe_lookup:    'linked_to',
  maigret_lookup:   'owns',
  spiderfoot_scan:  'linked_to',
  sherlock_lookup:  'owns',
  death_search:     'linked_to',
  crtsh_lookup:     'owns',
  urlscan_lookup:   'linked_to',
  virustotal_lookup:'linked_to',
  otx_lookup:       'linked_to',
  ipinfo_lookup:    'linked_to',
  image_investigation: 'linked_to',
  nominatim_geocode: 'linked_to',
  web_search_assistants: 'linked_to',
  social_web_search: 'linked_to',
  forum_search_assistants: 'linked_to',
  vehicle_plate_search: 'linked_to',
}

function mapResultNodeType(raw: string): NodeType {
  const t = raw.toLowerCase()
  if (ALL_NODE_TYPES.includes(t as NodeType)) return t as NodeType
  if (t === 'url') return 'domain'
  if (t === 'social_account') return 'social_account'
  return 'domain'
}

interface ResultCard {
  title?: string
  url: string
  snippet?: string
  source_engine?: string
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
  requires_api_key?: boolean
  configured?: boolean
  env_keys?: string[]
  api_key_help?: ApiKeyHelpItem[]
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
  result_cards?: ResultCard[]
  search_assistants?: Array<{ name: string; url: string }>
}

interface TransformEventBase {
  transform: string
  node_id?: string | null
}

interface TransformLogEvent extends TransformEventBase {
  message: string
  current?: number
  total?: number
}

interface TransformResultEvent extends TransformEventBase, TransformResult {}

interface TransformErrorEvent extends TransformEventBase {
  error: string
}

interface ActiveRun {
  transformId: string
  nodeId: string
}

interface TransformPanelProps {
  node: NodeData
}

export const TransformPanel: React.FC<TransformPanelProps> = ({ node }) => {
  const [transforms, setTransforms] = useState<Transform[]>([])
  const [running, setRunning] = useState<string | null>(null)
  const [logs, setLogs] = useState<string[]>([])
  const [progress, setProgress] = useState<{ current: number; total: number } | null>(null)
  const [forumKeywords, setForumKeywords] = useState('reddit,forum,leak,pirate,breach,credential')
  const [resultCards, setResultCards] = useState<ResultCard[]>([])
  const [searchAssistants, setSearchAssistants] = useState<Array<{ name: string; url: string }>>([])
  const { updateNode } = useGraphStore()
  const { t } = useTranslation()

  const activeRunRef = useRef<ActiveRun | null>(null)
  const restCompletedRef = useRef(false)
  const mergedNodeCountRef = useRef(0)

  const isActiveEvent = useCallback((data: TransformEventBase) => {
    const active = activeRunRef.current
    if (!active) return false
    return data.transform === active.transformId && data.node_id === active.nodeId
  }, [])

  const appendLog = useCallback((line: string) => {
    setLogs(prev => (prev.includes(line) ? prev : [...prev, line]))
  }, [])

  const mergeTransformResult = useCallback((
    transform: Transform,
    data: TransformResult,
  ) => {
    const edgeType = resolveEdgeType(transform.id, transform.output_types[0]?.toLowerCase() || 'linked_to')
    const newNodeObjects: NodeData[] = data.nodes.map(n =>
      createNode(mapResultNodeType(n.type), n.label, n.properties ?? {})
    )
    const newEdgeObjects: EdgeData[] = newNodeObjects.map(n =>
      createEdge(node.id, n.id, edgeType)
    )
    useGraphStore.getState().mergeNodes(newNodeObjects, newEdgeObjects)
    mergedNodeCountRef.current = data.nodes.length
  }, [node.id])

  useEffect(() => {
    apiClient.get('/transforms').then(res => {
      if (res.ok && res.data) {
        const nodeInput = node.type === 'plate' ? 'vehicle_plate' : node.type.toLowerCase()
        const compatible = (res.data as Transform[]).filter(
          t => t.input_types && (t.input_types.includes('*') || t.input_types.some(type => type.toLowerCase() === nodeInput))
        )
        setTransforms(compatible)
      }
    }).catch((err) => {
      console.error(err)
      setTransforms([])
    })
  }, [node.type])

  useEffect(() => {
    getSocket()

    const onStart = (data: TransformEventBase) => {
      if (!isActiveEvent(data)) return
      const tf = transforms.find(t => t.id === data.transform)
      appendLog(t('transforms.started', { name: tf?.name ?? data.transform }))
    }

    const onLog = (data: TransformLogEvent) => {
      if (!isActiveEvent(data)) return
      if (data.message) appendLog(data.message)
      if (data.current != null && data.total != null && data.total > 0) {
        setProgress({ current: data.current, total: data.total })
      }
    }

    const onResult = (data: TransformResultEvent) => {
      if (!isActiveEvent(data) || restCompletedRef.current) return
      const transform = transforms.find(tf => tf.id === data.transform)
      if (!transform) return

      mergeTransformResult(transform, data)
      if (data.result_cards?.length) setResultCards(data.result_cards)
      if (data.search_assistants?.length) {
        setSearchAssistants(data.search_assistants.map(a => ({ name: a.name, url: a.url })))
      }
      if (data.log?.length) {
        setLogs(prev => {
          const merged = [...prev]
          for (const line of data.log) {
            if (!merged.includes(line)) merged.push(line)
          }
          return merged
        })
      }
      appendLog(t('transforms.done', { count: data.nodes.length }))
      setRunning(null)
      setProgress(null)
      activeRunRef.current = null
    }

    const onError = (data: TransformErrorEvent) => {
      if (!isActiveEvent(data)) return
      appendLog(t('transforms.error', { message: data.error }))
      setRunning(null)
      setProgress(null)
      activeRunRef.current = null
    }

    wsClient.on('transform:start', onStart)
    wsClient.on('transform:log', onLog)
    wsClient.on('transform:progress', onLog)
    wsClient.on('transform:result', onResult)
    wsClient.on('transform:error', onError)

    return () => {
      wsClient.off('transform:start', onStart)
      wsClient.off('transform:log', onLog)
      wsClient.off('transform:progress', onLog)
      wsClient.off('transform:result', onResult)
      wsClient.off('transform:error', onError)
    }
  }, [appendLog, isActiveEvent, mergeTransformResult, t, transforms])

  const runTransform = async (transform: Transform) => {
    activeRunRef.current = { transformId: transform.id, nodeId: node.id }
    restCompletedRef.current = false
    mergedNodeCountRef.current = 0
    setRunning(transform.id)
    setLogs([t('transforms.starting', { name: transform.name })])
    setResultCards([])
    setSearchAssistants([])
    setProgress(null)

    try {
      const options: Record<string, unknown> = {}
      if (transform.id === 'forum_search_assistants') {
        options.keywords = forumKeywords.split(',').map(s => s.trim()).filter(Boolean)
      }
      const res = await apiClient.post('/transforms/run', {
        transform: transform.id,
        input_type: node.type === 'plate' ? 'vehicle_plate' : node.type,
        value: node.label,
        node_id: node.id,
        options,
      })

      restCompletedRef.current = true

      if (res.ok && res.data) {
        const data = res.data as TransformResult & { ok?: boolean; error?: string }
        if (data.result_cards?.length) setResultCards(data.result_cards)
        if (data.search_assistants?.length) {
          setSearchAssistants(data.search_assistants.map(a => ({ name: a.name, url: a.url })))
        }
        if (mergedNodeCountRef.current === 0) {
          mergeTransformResult(transform, data)
        }
        setLogs(prev => {
          const merged = [...prev]
          for (const line of data.log ?? []) {
            if (!merged.includes(line)) merged.push(line)
          }
          if (!merged.some(l => l.includes(String(data.nodes.length)))) {
            merged.push(t('transforms.done', { count: data.nodes.length }))
          }
          return merged
        })

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
      } else {
        const errMsg = (res.data as { error?: string })?.error ?? res.error ?? 'Unknown error'
        appendLog(t('transforms.error', { message: errMsg }))
        updateNode(node.id, {
          transformHistory: [
            ...(node.transformHistory ?? []),
            {
              transformName: transform.name,
              ranAt: new Date().toISOString(),
              resultCount: 0,
              status: 'error',
              error: errMsg,
            },
          ],
        })
      }
    } catch (err: unknown) {
      restCompletedRef.current = true
      const message = err instanceof Error ? err.message : String(err)
      appendLog(t('transforms.error', { message }))
      updateNode(node.id, {
        transformHistory: [
          ...(node.transformHistory ?? []),
          {
            transformName: transform.name,
            ranAt: new Date().toISOString(),
            resultCount: 0,
            status: 'error',
            error: message,
          },
        ],
      })
    } finally {
      setRunning(null)
      setProgress(null)
      activeRunRef.current = null
    }
  }

  const progressPct = progress && progress.total > 0
    ? Math.min(100, Math.round((progress.current / progress.total) * 100))
    : null

  return (
    <div className="transform-panel">
      {transforms.length === 0 && (
        <div className="node-list-empty" style={{ padding: '20px 16px' }}>
          {t('transforms.noTransforms', { type: node.type })}
        </div>
      )}

      {transforms.some(t => t.id === 'forum_search_assistants') && (
        <div className="transform-forum-kw">
          <label htmlFor="forum-kw">{t('transforms.forumKeywords')}</label>
          <input
            id="forum-kw"
            value={forumKeywords}
            onChange={e => setForumKeywords(e.target.value)}
            placeholder="reddit, pirate, leak…"
          />
        </div>
      )}

      <div className="transform-list">
        {transforms.map(tf => (
          <div key={tf.id} className="transform-item">
            <div className="transform-info">
              <div className="transform-name">{tf.name}</div>
              <div className="transform-desc">{tf.description}</div>
              {tf.requires_api_key && !tf.configured && (
                <div className="transform-api-key-row">
                  <div className="transform-api-hint">{t('transforms.apiKeyRequired', { keys: (tf.env_keys ?? []).join(', ') })}</div>
                  <ApiKeyHelp
                    items={tf.api_key_help ?? (tf.env_keys ?? []).map(k => ({ env_key: k }))}
                    variant="compact"
                  />
                </div>
              )}
            </div>
            <button
              className={`btn btn-primary transform-run-btn ${running === tf.id ? 'loading' : ''}`}
              onClick={() => runTransform(tf)}
              disabled={running !== null || (tf.requires_api_key === true && tf.configured === false)}
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

      {running && progressPct != null && (
        <div className="transform-progress" role="progressbar" aria-valuenow={progressPct}>
          <div className="transform-progress-bar" style={{ width: `${progressPct}%` }} />
          <span className="transform-progress-label">
            {t('transforms.progress', { pct: progressPct })}
          </span>
        </div>
      )}

      {resultCards.length > 0 && (
        <div className="transform-result-cards">
          <div className="transform-result-cards-title">{t('transforms.resultCardsTitle')}</div>
          {resultCards.map((card, i) => (
            <a
              key={`${card.url}-${i}`}
              className="transform-result-card"
              href={card.url}
              target="_blank"
              rel="noopener noreferrer"
            >
              <div className="transform-result-card-title">{card.title || card.url}</div>
              {card.snippet && <div className="transform-result-card-snippet">{card.snippet}</div>}
              <div className="transform-result-card-meta">{card.source_engine ?? card.url}</div>
            </a>
          ))}
        </div>
      )}

      {searchAssistants.length > 0 && resultCards.length === 0 && (
        <div className="transform-assistants-hint">
          <p>{t('transforms.assistantsHint')}</p>
          <div className="transform-assistants-links">
            {searchAssistants.slice(0, 4).map(a => (
              <a key={a.url} href={a.url} target="_blank" rel="noopener noreferrer">{a.name}</a>
            ))}
          </div>
        </div>
      )}

      {logs.length > 0 && (
        <div className="transform-log">
          {logs.map((l, i) => <div key={i} className="log-line">{l}</div>)}
        </div>
      )}
    </div>
  )
}
