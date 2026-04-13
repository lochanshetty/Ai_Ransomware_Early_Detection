import { useEffect, useState } from 'react'
import { Clock3, LayoutDashboard, ShieldCheck, ShieldX, Siren } from 'lucide-react'
import PageShell from '../components/layout/PageShell'
import GlassCard from '../components/ui/GlassCard'
import LoadingScreen from '../components/ui/LoadingScreen'
import { getAlerts, getMonitorLogs, getMonitorStatus, getThreats, runDemoAttack, startMonitoring } from '../services/crdsApi'

function DashboardPage() {
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)
  const [status, setStatus] = useState(null)
  const [alerts, setAlerts] = useState([])
  const [threats, setThreats] = useState([])
  const [logs, setLogs] = useState([])
  const [message, setMessage] = useState('')

  const refreshData = async () => {
    const [statusData, alertsData, threatsData, logsData] = await Promise.all([
      getMonitorStatus(),
      getAlerts(),
      getThreats(),
      getMonitorLogs(),
    ])
    setStatus(statusData)
    setAlerts(alertsData)
    setThreats(threatsData)
    setLogs(logsData)
    setLoading(false)
  }

  useEffect(() => {
    let mounted = true
    const loadOnMount = async () => {
      const [statusData, alertsData, threatsData, logsData] = await Promise.all([
        getMonitorStatus(),
        getAlerts(),
        getThreats(),
        getMonitorLogs(),
      ])
      if (!mounted) return
      setStatus(statusData)
      setAlerts(alertsData)
      setThreats(threatsData)
      setLogs(logsData)
      setLoading(false)
    }
    loadOnMount()
    return () => {
      mounted = false
    }
  }, [])

  useEffect(() => {
    const timer = setInterval(async () => {
      const [statusData, alertsData, threatsData, logsData] = await Promise.all([
        getMonitorStatus(),
        getAlerts(),
        getThreats(),
        getMonitorLogs(),
      ])
      setStatus(statusData)
      setAlerts(alertsData)
      setThreats(threatsData)
      setLogs(logsData)
    }, 8000)
    return () => clearInterval(timer)
  }, [])

  if (loading) return <LoadingScreen />

  const systemLabel = !status?.is_running ? 'SAFE' : threats.some((item) => item.threat_level === 'HIGH') ? 'ALERT' : 'MONITORING'
  const systemColor = systemLabel === 'ALERT' ? 'text-rose-300' : systemLabel === 'MONITORING' ? 'text-amber-300' : 'text-emerald-300'

  const handleStartMonitor = async () => {
    setBusy(true)
    await startMonitoring()
    await refreshData()
    setBusy(false)
  }

  const handleRunDemo = async () => {
    setBusy(true)
    const response = await runDemoAttack()
    setMessage(response.status || 'Demo completed')
    await refreshData()
    setBusy(false)
  }

  return (
    <PageShell title="Dashboard / Overview" icon={<LayoutDashboard className="h-3.5 w-3.5" />}>
      <div className="space-y-5">
        <h2 className="text-2xl font-semibold tracking-wide text-slate-100">DASHBOARD</h2>
        <div className="grid gap-3 md:grid-cols-4">
          <GlassCard className="min-h-[122px] xl-kpi-card">
            <div>
              <p className="text-xs uppercase tracking-[0.22em] text-cyan-300/80">System Status</p>
              <h2 className={`mt-2 text-3xl font-semibold ${systemColor}`}>{systemLabel}</h2>
              <p className="mt-2 text-sm text-slate-400">Session: {status?.run_id || 'none'}</p>
            </div>
          </GlassCard>
          <GlassCard className="min-h-[122px] xl-kpi-card">
            <p className="text-xs uppercase tracking-[0.22em] text-cyan-300/80">Threats Blocked</p>
            <h2 className="mt-2 text-3xl font-semibold text-rose-300">{threats.length}</h2>
            <p className="mt-2 text-xs text-slate-400">Detected incidents</p>
          </GlassCard>
          <GlassCard className="min-h-[122px] xl-kpi-card">
            <p className="text-xs uppercase tracking-[0.22em] text-cyan-300/80">Active Honeypots</p>
            <h2 className="mt-2 text-3xl font-semibold text-emerald-300">8</h2>
            <p className="mt-2 text-xs text-slate-400">All operational</p>
          </GlassCard>
          <GlassCard className="min-h-[122px] xl-kpi-card">
            <p className="text-xs uppercase tracking-[0.22em] text-cyan-300/80">Monitor Control</p>
            <button
              type="button"
              onClick={handleStartMonitor}
              disabled={busy}
              className="mt-2 w-full rounded-lg border border-cyan-400/40 bg-cyan-500/20 px-3 py-2 text-sm font-medium text-cyan-100 transition hover:bg-cyan-500/30 disabled:opacity-60"
            >
              {busy ? 'Starting...' : 'Start Monitoring'}
            </button>
            <button
              type="button"
              onClick={handleRunDemo}
              disabled={busy}
              className="mt-2 w-full rounded-lg border border-violet-400/40 bg-violet-500/20 px-3 py-2 text-sm font-medium text-violet-100 transition hover:bg-violet-500/30 disabled:opacity-60"
            >
              {busy ? 'Running...' : 'Run Demo Attack'}
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
                  <p className="text-xs uppercase tracking-wider text-slate-400">{alert.status}</p>
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
