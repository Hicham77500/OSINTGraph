import { NodeData, EdgeData } from '../graph/nodeTypes'

export function exportToJson(nodes: NodeData[], edges: EdgeData[]): string {
  return JSON.stringify({ nodes, edges }, null, 2)
}

export function exportToCsv(nodes: NodeData[], edges: EdgeData[]): string {
  // We'll export nodes as CSV.
  // Columns: id, type, label, properties
  const header = ['id', 'type', 'label', 'properties']
  const rows = nodes.map(n => {
    const props = JSON.stringify(n.properties || {}).replace(/"/g, '""')
    return `"${n.id}","${n.type}","${n.label.replace(/"/g, '""')}","${props}"`
  })
  return [header.join(','), ...rows].join('\n')
}

export function exportToMarkdown(nodes: NodeData[], edges: EdgeData[]): string {
  let md = '# OSINTGraph Export\n\n'
  
  md += '## Nodes\n\n'
  if (nodes.length === 0) {
    md += 'No nodes.\n\n'
  } else {
    nodes.forEach(n => {
      md += `- **${n.label}** (${n.type}) \`id: ${n.id}\`\n`
      const props = Object.entries(n.properties || {})
      if (props.length > 0) {
        props.forEach(([k, v]) => {
          md += `  - ${k}: ${v}\n`
        })
      }
    })
    md += '\n'
  }

  md += '## Edges\n\n'
  if (edges.length === 0) {
    md += 'No edges.\n\n'
  } else {
    edges.forEach(e => {
      const sourceNode = nodes.find(n => n.id === e.source)
      const targetNode = nodes.find(n => n.id === e.target)
      const sourceLabel = sourceNode ? sourceNode.label : e.source
      const targetLabel = targetNode ? targetNode.label : e.target
      md += `- ${sourceLabel} --[${e.type}]--> ${targetLabel}\n`
    })
    md += '\n'
  }

  return md
}

export function downloadStringAsFile(content: string, filename: string, mimeType: string) {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}
