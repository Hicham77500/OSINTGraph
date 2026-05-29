import type { Translations } from './en'

const fr: Translations = {
  // ── Brand / Toolbar ──────────────────────────────────────
  toolbar: {
    hideEntityPanel:  'Masquer le panneau entités',
    showEntityPanel:  'Afficher le panneau entités',
    undo:             'Annuler (Ctrl+Z)',
    redo:             'Rétablir (Ctrl+Y)',
    layoutForce:      'Disposition force',
    layoutHierarchy:  'Disposition hiérarchique',
    layoutGrid:       'Disposition grille',
    import:           'Importer',
    importTooltip:    'Importer CSV / JSON',
    save:             'Sauvegarder',
    saveTooltip:      'Sauvegarder le graphe',
    searchPlaceholder:'Rechercher des nœuds…',
    nodes_one:        '{{count}} nœud',
    nodes_other:      '{{count}} nœuds',
    edges_one:        '{{count}} lien',
    edges_other:      '{{count}} liens',
    connect:           'Relier',
    connectTooltip:    'Tracer un lien manuel entre deux noeuds',
    hideInspector:    "Masquer l'inspecteur",
    showInspector:    "Afficher l'inspecteur",
  },

  // ── Entity Panel ─────────────────────────────────────────
  entityPanel: {
    title:          'Entités',
    sectionTypes:   'Types',
    sectionInGraph: 'Dans le graphe',
    filterPlaceholder: 'Filtrer…',
    noNodes:        'Aucun nœud pour le moment',
    addTooltip:     'Ajouter {{label}}',
    addPlaceholder: 'Valeur de {{label}}…',
    addButton:      'Ajouter',
  },

  // ── Node Types ───────────────────────────────────────────
  nodeTypes: {
    person:       { label: 'Personne',         description: 'Une identité individuelle réelle ou supposée' },
    email:        { label: 'E-mail',           description: 'Une adresse e-mail' },
    domain:       { label: 'Domaine',          description: 'Un nom de domaine ou sous-domaine' },
    ip:           { label: 'Adresse IP',       description: 'Adresse IPv4 ou IPv6' },
    username:     { label: "Nom d'utilisateur", description: "Un pseudonyme ou handle sur une plateforme" },
    organization: { label: 'Organisation',     description: 'Une entreprise, un groupe ou une institution' },
  },

  // ── Edge Types ───────────────────────────────────────────
  edgeTypes: {
    owns:        'Possède',
    linked_to:   'Lié à',
    resolves_to: 'Résout vers',
    uses:        'Utilise',
  },

  // ── Inspector Panel ──────────────────────────────────────
  inspector: {
    title:          'Inspecteur',
    empty:          'Sélectionnez un nœud ou un lien à inspecter',
    edgeTitle:      'Lien',
    deleteNode:     'Supprimer le nœud',
    deleteEdge:     'Supprimer le lien',
    confidence:     'Confiance',
    tabProperties:  'Propriétés',
    tabTransforms:  'Transformations',
    tabHistory:     'Historique',
    propSource:     'Source',
    propCreated:    'Créé le',
    propTags:       'Étiquettes',
    noHistory:      "Aucun historique de transformation",
    historyResults: '{{count}} résultat(s)',
  },

  // ── Transform Panel ──────────────────────────────────────
  transforms: {
    noTransforms: 'Aucune transformation disponible pour {{type}}',
    run:          'Lancer',
    starting:     '[▶] {{name}} — démarrage…',
    done:         '✓ {{count}} résultat(s) trouvé(s)',
    error:        '✗ Erreur : {{message}}',
    catalog: {
      dns_lookup:    { display_name: 'Lookup DNS',      description: 'Résoudre un domaine vers ses adresses IP via DNS' },
      whois_lookup:  { display_name: 'Lookup Whois',    description: "Récupérer les données d'enregistrement Whois du domaine" },
      hibp_lookup:   { display_name: 'HaveIBeenPwned',  description: "Vérifier si l'e-mail figure dans des bases de violations connues" },
      shodan_lookup: { display_name: 'Lookup Shodan',   description: "Découvrir les ports et services ouverts d'une IP via Shodan" },
      sherlock_lookup: { display_name: 'Sherlock — Profils sociaux', description: 'Rechercher le pseudo sur 378+ réseaux sociaux (sherlock-project)' },
      holehe_lookup:   { display_name: 'Holehe — Comptes e-mail',   description: "Trouver les comptes enregistrés avec cet e-mail (120+ services)" },
    },
  },

  // ── Context Menu ────────────────────────────────────────── ─────────────────────────────────────────
  contextMenu: {
    inspectNode:      'Inspecter le nœud',
    copyValue:        'Copier la valeur',
    deleteNode:       'Supprimer le nœud',
    deleteEdge:       'Supprimer le lien',
    canvas:           'Canevas',
    newInvestigation: 'Nouvelle enquête',
  },

  // ── Import Modal ─────────────────────────────────────────
  importModal: {
    title:          'Importer des données',
    dropLabel:      'Déposez un fichier CSV ou JSON',
    dropSub:        'ou cliquez pour parcourir',
    previewSection: 'Aperçu et mappage des colonnes',
    ignore:         '— ignorer —',
    importButton:   'Importer',
    cancel:         'Annuler',
  },

  // ── Graph Canvas ─────────────────────────────────────────
  canvas: {
    connectPickSource: 'Cliquez sur le noeud source',
    connectPickTarget: 'Cliquez maintenant sur le noeud cible',
    connectChooseType: 'Choisir le type de relation',
    connectCancel:     'Annuler',
    emptyTitle: 'Démarrez votre enquête',
    emptyDesc:  'Ajoutez une entité depuis le panneau gauche, ou importez un fichier CSV / JSON',
  },
}

export default fr
