import { useEffect, useState } from 'react'
import { Clock3, LayoutDashboard, ShieldCheck, ShieldX, Siren } from 'lucide-react'
import PageShell from '../components/layout/PageShell'
import GlassCard from '../components/ui/GlassCard'
import LoadingScreen from '../components/ui/LoadingScreen'
import {
  getAlerts,
  getMonitorLogs,
  getMonitorStatus,
  getHoneypotStatus,
  getModelInfo,
  getSystemStatus,
  getThreats,
  systemRunAttack,
  systemStartMonitoring,
  systemStopAttack,
  systemStopMonitoring,
} from '../services/crdsApi'

function DashboardPage() {
  const [loading, setLoading] = useState(true)
  const [action, setAction] = useState('')
  const [status, setStatus] = useState(null)
  const [systemState, setSystemState] = useState({ monitoring: 'stopped', attack: 'stopped' })
  const [alerts, setAlerts] = useState([])
  const [threats, setThreats] = useState([])
  const [logs, setLogs] = useState([])
  const [honeypots, setHoneypots] = useState({ total_files: 0, triggered_files: 0, safe_files: 0 })
  const [modelInfo, setModelInfo] = useState(null)

  const refreshData = async () => {
    const [statusData, systemData, alertsData, threatsData, logsData, honeypotData, modelData] = await Promise.all([
      getMonitorStatus(),
      getSystemStatus(),
      getAlerts(),
      getThreats(),
      getMonitorLogs(),
      getHoneypotStatus(),
      getModelInfo(),
    ])
    setStatus(statusData)
    setSystemState(systemData)
    setAlerts(alertsData)
    setThreats(threatsData)
    setLogs(logsData)
    setHoneypots(honeypotData)
    setModelInfo(modelData)
    setLoading(false)
  }

  useEffect(() => {
    let mounted = true
    const loadOnMount = async () => {
      const [statusData, systemData, alertsData, threatsData, logsData, honeypotData, modelData] = await Promise.all([
        getMonitorStatus(),
        getSystemStatus(),
        getAlerts(),
        getThreats(),
        getMonitorLogs(),
        getHoneypotStatus(),
        getModelInfo(),
      ])
      if (!mounted) return
      setStatus(statusData)
      setSystemState(systemData)
      setAlerts(alertsData)
      setThreats(threatsData)
      setLogs(logsData)
      setHoneypots(honeypotData)
      setModelInfo(modelData)
      setLoading(false)
    }
    loadOnMount()
    return () => {
      mounted = false
    }
  }, [])

  useEffect(() => {
    const timer = setInterval(async () => {
      const [statusData, systemData, alertsData, threatsData, logsData, honeypotData, modelData] = await Promise.all([
        getMonitorStatus(),
        getSystemStatus(),
        getAlerts(),
        getThreats(),
        getMonitorLogs(),
        getHoneypotStatus(),
        getModelInfo(),
      ])
      setStatus(statusData)
      setSystemState(systemData)
      setAlerts(alertsData)
      setThreats(threatsData)
      setLogs(logsData)
      setHoneypots(honeypotData)
      setModelInfo(modelData)
    }, 2000)
    return () => clearInterval(timer)
  }, [])

  if (loading) return <LoadingScreen />

  const monitoringRunning = systemState.monitoring === 'running'
  const attackRunning = systemState.attack === 'running'
  const systemLabel = attackRunning ? 'ALERT' : monitoringRunning ? 'MONITORING' : 'SAFE'
  const systemColor = systemLabel === 'ALERT' ? 'text-rose-300' : systemLabel === 'MONITORING' ? 'text-amber-300' : 'text-emerald-300'
  const panelGlow = attackRunning ? 'shadow-[0_0_34px_rgba(251,113,133,0.45)] border-rose-400/40' : 'border-cyan-300/20'

  const handleStartMonitor = async () => {
    setAction('start-monitoring')
    const response = await systemStartMonitoring()
    setMessage(response.message || 'Monitoring started')
    await refreshData()
    setAction('')
  }

  const handleStopMonitor = async () => {
    setAction('stop-monitoring')
    const response = await systemStopMonitoring()
    setMessage(response.message || 'Monitoring stopped')
    await refreshData()
    setAction('')
  }

  const handleRunDemo = async () => {
    setAction('run-attack')
    const response = await systemRunAttack()
    setMessage(response.message || 'Attack started')
    await refreshData()
    setAction('')
  }

  const handleStopAttack = async () => {
    setAction('stop-attack')
    const response = await systemStopAttack()
    setMessage(response.message || 'Attack Stopped')
    await refreshData()
    setAction('')
  }

  return (
    <PageShell title="Dashboard / Overview" icon={<LayoutDashboard className="h-3.5 w-3.5" />}>
      <div className="space-y-5">
        <h2 className="text-2xl font-semibold tracking-wide text-slate-100">DASHBOARD</h2>
        <div className="grid gap-3 md:grid-cols-4">
          <GlassCard className={`min-h-[122px] xl-kpi-card ${panelGlow}`}>
            <div>
              <p className="text-xs uppercase tracking-[0.22em] text-cyan-300/80">System Status</p>
              <h2 className={`mt-2 text-3xl font-semibold ${systemColor}`}>{systemLabel}</h2>
              <p className="mt-2 text-sm text-slate-400">Session: {status?.run_id || 'none'}</p>
              <p className="mt-1 text-xs text-slate-300">
                Monitoring: {systemState.monitoring} | Attack: {systemState.attack}
              </p>
            </div>
          </GlassCard>
          <GlassCard className="min-h-[122px] xl-kpi-card">
            <p className="text-xs uppercase tracking-[0.22em] text-cyan-300/80">Threats Blocked</p>
            <h2 className="mt-2 text-3xl font-semibold text-rose-300">{threats.length}</h2>
            <p className="mt-2 text-xs text-slate-400">Detected incidents</p>
          </GlassCard>
          <GlassCard className="min-h-[122px] xl-kpi-card">
            <p className="text-xs uppercase tracking-[0.22em] text-cyan-300/80">Active Honeypots</p>
            <h2 className="mt-2 text-3xl font-semibold text-emerald-300">{honeypots.total_files}</h2>
            <p className="mt-2 text-xs text-slate-400">
              {honeypots.triggered_files > 0
                ? `${honeypots.triggered_files} triggered`
                : 'All operational'}
            </p>
          </GlassCard>
          <GlassCard className="min-h-[122px] xl-kpi-card">
            <p className="text-xs uppercase tracking-[0.22em] text-cyan-300/80">System Controls</p>
            <button
              type="button"
              onClick={handleStartMonitor}
              disabled={action !== '' || monitoringRunning}
              className="mt-2 w-full rounded-lg border border-cyan-400/40 bg-cyan-500/20 px-3 py-2 text-sm font-medium text-cyan-100 transition hover:bg-cyan-500/30 disabled:opacity-60"
            >
              {action === 'start-monitoring' ? 'Running...' : 'Start Monitoring'}
            </button>
            <button
              type="button"
              onClick={handleStopMonitor}
              disabled={action !== '' || !monitoringRunning}
              className="mt-2 w-full rounded-lg border border-slate-300/30 bg-slate-800/60 px-3 py-2 text-sm font-medium text-slate-100 transition hover:bg-slate-700/70 disabled:opacity-60"
            >
              {action === 'stop-monitoring' ? 'Stopping...' : 'Stop Monitoring'}
            </button>
            <button
              type="button"
              onClick={handleRunDemo}
              disabled={action !== '' || attackRunning}
              className="mt-2 w-full rounded-lg border border-violet-400/40 bg-violet-500/20 px-3 py-2 text-sm font-medium text-violet-100 transition hover:bg-violet-500/30 disabled:opacity-60"
            >
              {action === 'run-attack' ? 'Launching...' : 'Run Demo Attack'}
            </button>
            <button
              type="button"
              onClick={handleStopAttack}
              disabled={action !== '' || !attackRunning}
              className="mt-2 w-full rounded-lg border border-rose-400/40 bg-rose-500/20 px-3 py-2 text-sm font-medium text-rose-100 transition hover:bg-rose-500/30 disabled:opacity-60"
            >
              {action === 'stop-attack' ? 'Stopping...' : 'Stop Attack'}
            </button>
          </GlassCard>
        </div>
        {message && (
          <GlassCard className="py-2">
            <p className="text-xs text-cyan-300">{message}</p>
          </GlassCard>
        )}

        <GlassCard className="py-3">
          <div className="flex items-center gap-3 rounded-xl border border-cyan-300/20 bg-slate-950/50 px-4 py-3 text-slate-300">
            <Clock3 className="h-4 w-4 text-cyan-300" />
            {status?.started_at ? new Date(status.started_at).toLocaleString() : 'Not started'}
            {monitoringRunning && <span className="status-pill success">LIVE</span>}
            {attackRunning && <span className="status-pill blocked">ATTACK ACTIVE</span>}
            {!attackRunning && monitoringRunning && <span className="status-pill warning">RECOVERED</span>}
          </div>
        </GlassCard>

        <div className="grid gap-3 lg:grid-cols-2">
          <GlassCard className="min-h-[280px] xl-panel">
            <h3 className="mb-4 flex items-center gap-2 text-lg font-semibold text-rose-200">
              <Siren className="h-5 w-5" /> Threat Alerts
            </h3>
            <div className="space-y-3">
              {threats.slice(0, 4).map((threat) => (
                <div key={threat.id} className="rounded-xl border border-rose-400/30 bg-rose-500/10 p-3 shadow-[0_0_18px_rgba(251,113,133,0.2)]">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium text-rose-200">{threat.threat_type || threat.threat_level}</p>
                    <span className="status-pill blocked">{threat.threat_level}</span>
                  </div>
                  <p className="text-xs text-slate-300">{threat.reason}</p>
                </div>
              ))}
              {threats.length === 0 && <p className="text-sm text-slate-400">No threats detected yet.</p>}
            </div>
          </GlassCard>

          <GlassCard className="min-h-[280px] xl-panel">
            <h3 className="mb-4 text-lg font-semibold text-cyan-100">Recent Logs</h3>
            <div className="space-y-2">
              {logs.slice(0, 6).map((log) => (
                <div key={log.id} className="flex items-start justify-between gap-3 rounded-lg border border-cyan-400/15 bg-slate-900/40 p-2">
                  <div>
                    <p className="text-sm text-slate-100">{(log.action || log.event_type).replace('_', ' ')}</p>
                    <p className="text-xs text-slate-400">{log.file_path || log.message}</p>
                  </div>
                  <span className="status-pill success">{log.action === 'rename' ? 'BLOCKED' : 'SUCCESS'}</span>
                </div>
              ))}
              {logs.length === 0 && <p className="text-sm text-slate-400">No monitoring logs yet.</p>}
            </div>
          </GlassCard>
        </div>

        <GlassCard>
          <h3 className="mb-4 text-lg font-semibold text-cyan-100">Alert Timeline</h3>
          <div className="space-y-3">
            {alerts.slice(0, 4).map((alert) => (
              <div key={alert.id} className="flex items-start gap-3">
                {alert.severity === 'high' ? (
                  <ShieldX className="mt-1 h-4 w-4 text-rose-300" />
                ) : (
                  <ShieldCheck className="mt-1 h-4 w-4 text-emerald-300" />
                )}
                <div>
                  <p className="text-sm text-slate-100">{alert.title}</p>
                  <p className="text-xs uppercase tracking-wider text-slate-400">{alert.status === 'open' ? 'ACTIVE' : 'RESOLVED'}</p>
                </div>
              </div>
            ))}
            {alerts.length === 0 && <p className="text-sm text-slate-400">No alerts yet.</p>}
          </div>
        </GlassCard>
      </div>
    </PageShell>
  )
}

export default DashboardPage
