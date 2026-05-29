const en = {
  // ── Brand / Toolbar ──────────────────────────────────────
  toolbar: {
    hideEntityPanel:  'Hide entity panel',
    showEntityPanel:  'Show entity panel',
    undo:             'Undo (Ctrl+Z)',
    redo:             'Redo (Ctrl+Y)',
    layoutForce:      'Force-directed layout',
    layoutHierarchy:  'Hierarchical layout',
    layoutGrid:       'Grid layout',
    import:           'Import',
    importTooltip:    'Import CSV / JSON',
    save:             'Save',
    saveTooltip:      'Save graph',
    searchPlaceholder:'Search nodes…',
    nodes_one:        '{{count}} node',
    nodes_other:      '{{count}} nodes',
    edges_one:        '{{count}} edge',
    edges_other:      '{{count}} edges',
    connect:          'Connect',
    connectTooltip:   'Draw a manual link between two nodes',
    hideInspector:    'Hide inspector',
    showInspector:    'Show inspector',
  },

  // ── Entity Panel ─────────────────────────────────────────
  entityPanel: {
    title:          'Entities',
    sectionTypes:   'Types',
    sectionInGraph: 'In graph',
    filterPlaceholder: 'Filter…',
    noNodes:        'No nodes yet',
    addTooltip:     'Add {{label}}',
    addPlaceholder: 'Enter {{label}} value…',
    addButton:      'Add',
  },

  // ── Node Types ───────────────────────────────────────────
  nodeTypes: {
    person:       { label: 'Person',       description: 'A real or suspected individual identity' },
    email:        { label: 'Email',        description: 'An email address' },
    domain:       { label: 'Domain',       description: 'A domain name or subdomain' },
    ip:           { label: 'IP Address',   description: 'IPv4 or IPv6 address' },
    username:     { label: 'Username',     description: 'A username or handle on a platform' },
    organization: { label: 'Organization', description: 'A company, group, or institution' },
  },

  // ── Edge Types ───────────────────────────────────────────
  edgeTypes: {
    owns:        'Owns',
    linked_to:   'Linked To',
    resolves_to: 'Resolves To',
    uses:        'Uses',
  },

  // ── Inspector Panel ──────────────────────────────────────
  inspector: {
    title:          'Inspector',
    empty:          'Select a node or edge to inspect',
    edgeTitle:      'Edge',
    deleteNode:     'Delete node',
    deleteEdge:     'Delete edge',
    confidence:     'Confidence',
    tabProperties:  'Properties',
    tabTransforms:  'Transforms',
    tabHistory:     'History',
    propSource:     'Source',
    propCreated:    'Created',
    propTags:       'Tags',
    noHistory:      'No transform history',
    historyResults: '{{count}} results',
  },

  // ── Transform Panel ──────────────────────────────────────
  transforms: {
    noTransforms: 'No transforms available for {{type}}',
    run:          'Run',
    starting:     '[▶] {{name}} — starting…',
    done:         '✓ {{count}} result(s) found',
    error:        '✗ Error: {{message}}',
    catalog: {
      dns_lookup:    { display_name: 'DNS Lookup',     description: 'Resolve domain to IP addresses via DNS' },
      whois_lookup:  { display_name: 'Whois Lookup',   description: 'Retrieve Whois registration data for a domain' },
      hibp_lookup:   { display_name: 'HaveIBeenPwned', description: 'Check if email appears in known breach databases' },
      shodan_lookup: { display_name: 'Shodan Lookup',  description: 'Discover open ports and services on an IP via Shodan' },
      sherlock_lookup: { display_name: 'Sherlock — Social Profiles', description: 'Search username across 378+ social networks (sherlock-project)' },
      holehe_lookup:   { display_name: 'Holehe — Email Accounts',   description: 'Find accounts registered with this email across 120+ services' },
    },
  },

  // ── Context Menu ─────────────────────────────────────────
  contextMenu: {
    inspectNode:   'Inspect node',
    copyValue:     'Copy value',
    deleteNode:    'Delete node',
    deleteEdge:    'Delete edge',
    canvas:        'Canvas',
    newInvestigation: 'New investigation',
  },

  // ── Import Modal ─────────────────────────────────────────
  importModal: {
    title:          'Import Data',
    dropLabel:      'Drop a CSV or JSON file',
    dropSub:        'or click to browse',
    previewSection: 'Preview & Column Mapping',
    ignore:         '— ignore —',
    importButton:   'Import',
    cancel:         'Cancel',
  },

  // ── Graph Canvas ─────────────────────────────────────────
  canvas: {
    connectPickSource: 'Click a source node',
    connectPickTarget: 'Now click the target node',
    connectChooseType: 'Choose relation type',
    connectCancel:     'Cancel',
    emptyTitle: 'Start your investigation',
    emptyDesc:  'Add an entity from the left panel, or import a CSV / JSON file',
  },
} as const

export default en
export type Translations = typeof en
