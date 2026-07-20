import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import en from './locales/en'
import fr from './locales/fr'

const savedLang = localStorage.getItem('osintgraph:lang') ?? 'en'

i18n
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: en },
      fr: { translation: fr },
    },
    lng: savedLang,
    fallbackLng: 'en',
    interpolation: {
      // React already handles XSS
      escapeValue: false,
    },
  })

i18n.on('languageChanged', (lng) => {
  localStorage.setItem('osintgraph:lang', lng)
})

export default i18n
