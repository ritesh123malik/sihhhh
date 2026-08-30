import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Launch from './pages/Launch/Launch'
import DetectionResults from './pages/DetectionResults/DetectionResults'
import Uploads from './pages/Uploads/Uploads'
import Reports from './pages/Reports/Reports'
import Map from './pages/Map/Map'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Launch />} />
        <Route path="/uploads" element={<Uploads />} />
        <Route path="/results" element={<Navigate to="/uploads" replace />} />
        <Route path="/results/:runId" element={<DetectionResults />} />
        <Route path="/reports" element={<Reports />} />
        <Route path="/map" element={<Map />} />
        <Route path="/settings" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
