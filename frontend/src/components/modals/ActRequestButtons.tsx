import React, { useState } from 'react'
import { Mail, ExternalLink, Info } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import type { DeathRecord } from '../../services/deathSearch'
import {
  buildActRequestMailto,
  getActRequestEligibility,
  getArchivesAnnuaireUrl,
  type ActKind,
} from '../../utils/civilRegistryRequest'

interface ActRequestButtonsProps {
  record: DeathRecord
}

export const ActRequestButtons: React.FC<ActRequestButtonsProps> = ({ record }) => {
  const { t } = useTranslation()
  const [filiationConfirmed, setFiliationConfirmed] = useState(false)
  const [showBirthConfirm, setShowBirthConfirm] = useState(false)

  const deathEligibility = getActRequestEligibility(record, 'death', { filiationJustified: false })
  const birthEligibility = getActRequestEligibility(record, 'birth', { filiationJustified: filiationConfirmed })

  const mailtoLabels = {
    subjectDeath: t('deathSearch.act.subjectDeath'),
    subjectBirth: t('deathSearch.act.subjectBirth'),
    bodyDeath: t('deathSearch.act.bodyDeath'),
    bodyBirth: t('deathSearch.act.bodyBirth'),
    filiationNote: t('deathSearch.act.filiationInBody'),
  }

  const openMailto = (kind: ActKind) => {
    const url = buildActRequestMailto(record, kind, mailtoLabels, {
      filiationJustified: kind === 'birth' && filiationConfirmed,
    })
    window.location.href = url
    setShowBirthConfirm(false)
  }

  const handleBirthClick = () => {
    if (birthEligibility.allowed) {
      openMailto('birth')
      return
    }
    if (birthEligibility.requiresFiliationProof) {
      setShowBirthConfirm(true)
    }
  }

  const confirmBirthRequest = () => {
    if (!filiationConfirmed) return
    const recheck = getActRequestEligibility(record, 'birth', { filiationJustified: true })
    if (recheck.allowed) openMailto('birth')
  }

  return (
    <div className="act-request-cell">
      <div className="act-request-buttons">
        <button
          type="button"
          className="btn btn-ghost btn-xs act-request-btn"
          disabled={!deathEligibility.allowed}
          title={t(deathEligibility.reasonKey)}
          onClick={() => openMailto('death')}
        >
          <Mail size={12} />
          {t('deathSearch.act.requestDeath')}
        </button>
        <button
          type="button"
          className="btn btn-ghost btn-xs act-request-btn"
          disabled={!birthEligibility.allowed && !birthEligibility.requiresFiliationProof}
          title={t(birthEligibility.reasonKey)}
          onClick={handleBirthClick}
        >
          <Mail size={12} />
          {t('deathSearch.act.requestBirth')}
        </button>
        <a
          href={getArchivesAnnuaireUrl(record)}
          target="_blank"
          rel="noopener noreferrer"
          className="btn btn-ghost btn-xs act-request-btn act-request-link"
          title={t('deathSearch.act.findArchives')}
        >
          <ExternalLink size={12} />
        </a>
      </div>

      {showBirthConfirm && (
        <div className="act-request-confirm">
          <p className="act-request-warning">
            <Info size={14} />
            {t('deathSearch.act.birthConfirmIntro')}
          </p>
          <label className="act-request-checkbox">
            <input
              type="checkbox"
              checked={filiationConfirmed}
              onChange={e => setFiliationConfirmed(e.target.checked)}
            />
            {t('deathSearch.act.filiationCheckbox')}
          </label>
          <div className="act-request-confirm-actions">
            <button
              type="button"
              className="btn btn-primary btn-xs"
              disabled={!filiationConfirmed}
              onClick={confirmBirthRequest}
            >
              {t('deathSearch.act.openMailClient')}
            </button>
            <button
              type="button"
              className="btn btn-ghost btn-xs"
              onClick={() => {
                setShowBirthConfirm(false)
                setFiliationConfirmed(false)
              }}
            >
              {t('deathSearch.act.cancel')}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
