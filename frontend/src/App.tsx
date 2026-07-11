import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { DossiersPage } from './pages/DossiersPage'
import { DossierPage } from './pages/DossierPage'
import { CarnetViewPage } from './pages/CarnetViewPage'
import { CarnetGraphPage } from './pages/CarnetGraphPage'
import { PersonViewPage } from './pages/PersonViewPage'
import { CommandSearch } from './components/search/CommandSearch'
import './pages/DossiersPage.css'

export default function App() {
  return (
    <BrowserRouter>
      <CommandSearch />
      <Routes>
        <Route path="/" element={<DossiersPage />} />
        <Route path="/dossier/:dossierId" element={<DossierPage />} />
        <Route path="/dossier/:dossierId/carnet/:carnetId" element={<CarnetViewPage />} />
        <Route path="/dossier/:dossierId/graph" element={<CarnetGraphPage />} />
        <Route path="/dossier/:dossierId/person/:entityId" element={<PersonViewPage />} />
      </Routes>
    </BrowserRouter>
  )
}
