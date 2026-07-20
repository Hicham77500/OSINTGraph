import { describe, it, expect, beforeEach } from 'vitest'
import { useGraphStore } from '../graph/graphStore'
import { createNode, createEdge } from '../graph/nodeTypes'

describe('graphStore', () => {
  beforeEach(() => {
    useGraphStore.setState({
      nodes: [],
      edges: [],
      selectedNodeId: null,
      selectedEdgeId: null,
      history: [{ nodes: [], edges: [], description: 'initial' }],
      historyIndex: 0,
    })
  })

  it('adds a node', () => {
    const node = useGraphStore.getState().addNode('person', 'John Doe')
    expect(useGraphStore.getState().nodes).toHaveLength(1)
    expect(node.label).toBe('John Doe')
    expect(node.type).toBe('person')
  })

  it('adds an edge between nodes', () => {
    const a = useGraphStore.getState().addNode('email', 'a@b.com')
    const b = useGraphStore.getState().addNode('domain', 'b.com')
    useGraphStore.getState().addEdge(a.id, b.id, 'linked_to')
    expect(useGraphStore.getState().edges).toHaveLength(1)
  })

  it('createNode factory sets metadata', () => {
    const node = createNode('username', 'shadow_92')
    expect(node.metadata?.source).toBe('manual')
    expect(node.label).toBe('shadow_92')
  })

  it('createEdge factory sets type label', () => {
    const edge = createEdge('a', 'b', 'uses')
    expect(edge.type).toBe('uses')
    expect(edge.label).toBeTruthy()
  })
})
