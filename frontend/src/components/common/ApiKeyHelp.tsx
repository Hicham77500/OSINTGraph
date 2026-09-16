import React, { useId, useState } from 'react'
import { ExternalLink, Info } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import './ApiKeyHelp.css'

export type ApiKeyHelpItem = {
  env_key: string
  provider?: string
  signup_url?: string | null
  docs_url?: string | null
}

interface ApiKeyHelpProps {
  items: ApiKeyHelpItem[]
  /** compact = icon-only trigger in tight layouts */
  variant?: 'inline' | 'compact'
  className?: string
}

export const ApiKeyHelp: React.FC<ApiKeyHelpProps> = ({
  items,
  variant = 'inline',
  className = '',
}) => {
  const { t } = useTranslation()
  const [open, setOpen] = useState(false)
  const panelId = useId()

  if (!items.length) return null

  const hasLinks = items.some(i => i.signup_url || i.docs_url)

  return (
    <div className={`api-key-help ${variant} ${className}`.trim()}>
      <button
        type="button"
        className="api-key-help-trigger"
        aria-expanded={open}
        aria-controls={panelId}
        title={t('transformHub.apiKey.infoTitle')}
        onClick={() => setOpen(v => !v)}
      >
        <Info size={variant === 'compact' ? 14 : 13} aria-hidden />
        {variant === 'inline' && (
          <span>{t('transformHub.apiKey.infoLabel')}</span>
        )}
      </button>
      {open && (
        <div id={panelId} className="api-key-help-panel" role="region" aria-label={t('transformHub.apiKey.panelLabel')}>
          <p className="api-key-help-intro">{t('transformHub.apiKey.intro')}</p>
          <ul className="api-key-help-list">
            {items.map(item => (
              <li key={item.env_key}>
                <div className="api-key-help-row-title">
                  <code>{item.env_key}</code>
                  {item.provider && (
                    <span className="api-key-help-provider">{item.provider}</span>
                  )}
                </div>
                {hasLinks ? (
                  <div className="api-key-help-links">
                    {item.signup_url && (
                      <a href={item.signup_url} target="_blank" rel="noopener noreferrer">
                        <ExternalLink size={11} aria-hidden />
                        {t('transformHub.apiKey.getKey')}
                      </a>
                    )}
                    {item.docs_url && (
                      <a href={item.docs_url} target="_blank" rel="noopener noreferrer">
                        <ExternalLink size={11} aria-hidden />
                        {t('transformHub.apiKey.docs')}
                      </a>
                    )}
                    {!item.signup_url && !item.docs_url && (
                      <span className="api-key-help-muted">{t('transformHub.apiKey.noLink')}</span>
                    )}
                  </div>
                ) : null}
              </li>
            ))}
          </ul>
          <p className="api-key-help-foot">{t('transformHub.apiKey.envHint')}</p>
        </div>
      )}
    </div>
  )
}
