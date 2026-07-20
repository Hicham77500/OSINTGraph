import React from 'react'
import { Globe } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import i18n from '../../i18n'
import './LanguageSwitcher.css'

interface LanguageSwitcherProps {
  className?: string
}

export const LanguageSwitcher: React.FC<LanguageSwitcherProps> = ({ className = '' }) => {
  const { t, i18n: i18nInstance } = useTranslation()
  const currentLang = i18nInstance.language.startsWith('fr') ? 'fr' : 'en'
  const toggleLang = () => i18n.changeLanguage(currentLang === 'fr' ? 'en' : 'fr')

  return (
    <button
      type="button"
      className={`btn btn-ghost lang-switcher ${className}`.trim()}
      onClick={toggleLang}
      data-tooltip={currentLang === 'fr' ? t('toolbar.switchToEnglish') : t('toolbar.switchToFrench')}
      aria-label={currentLang === 'fr' ? t('toolbar.switchToEnglish') : t('toolbar.switchToFrench')}
    >
      <Globe size={13} />
      <span className="lang-label">{currentLang.toUpperCase()}</span>
    </button>
  )
}
