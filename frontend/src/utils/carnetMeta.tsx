import React from 'react'
import {
  User, Building2, AtSign, Share2, Clock, StickyNote, BookOpen, GitGraph,
} from 'lucide-react'

export function carnetIcon(notebookType: string, size = 18): React.ReactNode {
  switch (notebookType) {
    case 'personnes': return <User size={size} />
    case 'reseaux_sociaux': return <Share2 size={size} />
    case 'entreprises': return <Building2 size={size} />
    case 'pseudonymes': return <AtSign size={size} />
    case 'chronologie': return <Clock size={size} />
    case 'notes': return <StickyNote size={size} />
    default: return <BookOpen size={size} />
  }
}

export function graphIcon(size = 22): React.ReactNode {
  return <GitGraph size={size} />
}

export function carnetDescriptionKey(notebookType: string): string {
  return `dossier.carnetDescriptions.${notebookType}`
}
