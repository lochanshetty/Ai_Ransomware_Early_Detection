import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import AppShell from './components/layout/AppShell'
import StartupDiagnostics from './components/ui/StartupDiagnostics'
import DashboardPage from './pages/DashboardPage'
import HoneypotPage from './pages/HoneypotPage'
import LoginPage from './pages/LoginPage'
import LogsPage from './pages/LogsPage'
import SignupPage from './pages/SignupPage'
import SystemStatusPage from './pages/SystemStatusPage'
import ThreatsPage from './pages/ThreatsPage'

function App() {
  return (
    <>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to="/login" replace />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route path="/app" element={<AppShell />}>
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="logs" element={<LogsPage />} />
            <Route path="threats" element={<ThreatsPage />} />
            <Route path="honeypots" element={<HoneypotPage />} />
            <Route path="status" element={<SystemStatusPage />} />
            <Route path="*" element={<Navigate to="/app/dashboard" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
      <StartupDiagnostics />
    </>
  )
}

export default App
