import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Layout } from './components/layout/Layout'
import { Dashboard } from './pages/Dashboard'
import { PlayerDetail } from './pages/PlayerDetail'
import { TradeFeed } from './pages/TradeFeed'
import { CramerPicks } from './pages/CramerPicks'
import { TaxReport } from './pages/TaxReport'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/player/:id" element={<PlayerDetail />} />
          <Route path="/trades" element={<TradeFeed />} />
          <Route path="/cramer" element={<CramerPicks />} />
          <Route path="/tax" element={<TaxReport />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
