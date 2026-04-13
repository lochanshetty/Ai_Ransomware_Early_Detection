import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Navbar from './components/Navbar'
import HoneypotPage from './pages/HoneypotPage'
import LogsPage from './pages/LogsPage'
import OverviewPage from './pages/OverviewPage'
import ThreatsPage from './pages/ThreatsPage'

function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<OverviewPage />} />
        <Route path="/logs" element={<LogsPage />} />
        <Route path="/threats" element={<ThreatsPage />} />
        <Route path="/honeypot" element={<HoneypotPage />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
