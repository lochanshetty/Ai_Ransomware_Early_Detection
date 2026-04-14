import { createElement } from 'react'
import { useEffect, useState } from 'react'
import { Activity, Cpu, Database, HardDrive, Radar, Shield, Wifi } from 'lucide-react'
import GlassCard from '../components/ui/GlassCard'
import PageShell from '../components/layout/PageShell'
import { getSystemMetrics } from '../services/crdsApi'

function SystemStatusPage() {
  const [payload, setPayload] = useState(null)
  const [selectedComponent, setSelectedComponent] = useState(null)
  const [history, setHistory] = useState({ cpu: [], mem: [], net: [] })

  useEffect(() => {
    const load = async () => {
      const data = await getSystemMetrics()
      setPayload(data)
      setHistory((prev) => ({
        cpu: [...prev.cpu.slice(-19), Number(data.metrics?.cpu_percent || 0)],
        mem: [...prev.mem.slice(-19), Number(data.metrics?.memory_percent || 0)],
        net: [...prev.net.slice(-19), Number(data.metrics?.network_bytes_recv || 0) / 1024 / 1024],
      }))
    }
    load()
    const timer = setInterval(load, 2000)
    return () => clearInterval(timer)
  }, [])

  const iconMap = {
    Firewall: Shield,
    'IDS/IPS': Radar,
    'Threat DB': Database,
    'ML Engine': Cpu,
    'Network Monitor': Wifi,
    Storage: HardDrive,
  }

  const telemetry = (payload?.components || []).map((component) => ({
    label: component.name,
    value: component.status,
    role: component.role,
    metrics: component.metrics,
    icon: iconMap[component.name] || Activity,
  }))

  const sparkline = (series, color) => (
    <div className="flex h-16 items-end gap-[2px]">
      {series.map((value, idx) => (
        <div key={`${color}-${idx}`} className={color} style={{ height: `${Math.max(6, value)}%`, width: `${100 / Math.max(1, series.length)}%` }} />
      ))}
    </div>
  )

  return (
    <PageShell title="Dashboard / System Status" icon={<Activity className="h-3.5 w-3.5" />}>
      <h2 className="mb-4 text-2xl font-semibold tracking-wide text-slate-100">SYSTEM STATUS</h2>
      <GlassCard className="mb-4 border-cyan-500/30">
        <p className="text-xl font-semibold text-cyan-300">
          {payload?.system?.attack === 'running' ? 'ATTACK ACTIVE' : payload?.system?.monitoring === 'running' ? 'MONITORING ACTIVE' : 'SAFE / RECOVERED'}
        </p>
        <p className="mt-1 text-xs text-slate-400">Uptime: 99.97% | Last scan: {new Date().toLocaleString()}</p>
      </GlassCard>
      <div className="grid gap-3 md:grid-cols-3">
        {telemetry.map(({ label, value, icon, role, metrics }) => (
          <GlassCard key={label} className="cursor-pointer" onClick={() => setSelectedComponent({ label, value, role, metrics })}>
            <div className="mb-2 flex items-center justify-between gap-2 text-cyan-200">
              <div className="flex items-center gap-2">
              {createElement(icon, { className: 'h-5 w-5' })}
              <p className="text-sm">{label}</p>
              </div>
              <span className={`status-pill ${value === 'ACTIVE' ? 'success' : 'warning'}`}>{value.toUpperCase()}</span>
            </div>
          </GlassCard>
        ))}
      </div>
      <div className="mt-3 grid gap-3 md:grid-cols-3">
        <GlassCard>
          <p className="text-xs text-cyan-300">CPU</p>
          <p className="text-4xl font-bold text-cyan-300">{Math.round(payload?.metrics?.cpu_percent || 0)}%</p>
          {sparkline(history.cpu, 'bg-cyan-400/80')}
        </GlassCard>
        <GlassCard>
          <p className="text-xs text-emerald-300">MEMORY</p>
          <p className="text-4xl font-bold text-emerald-300">{Math.round(payload?.metrics?.memory_percent || 0)}%</p>
          {sparkline(history.mem, 'bg-emerald-400/80')}
        </GlassCard>
        <GlassCard>
          <p className="text-xs text-violet-300">NETWORK</p>
          <p className="text-4xl font-bold text-violet-300">{(Number(payload?.metrics?.network_bytes_recv || 0) / 1024 / 1024).toFixed(1)} MB</p>
          {sparkline(history.net, 'bg-violet-400/80')}
        </GlassCard>
      </div>
      {selectedComponent && (
        <GlassCard className="mt-4 border border-cyan-300/30">
          <div className="mb-2 flex items-center justify-between">
            <p className="text-sm font-semibold text-cyan-100">{selectedComponent.label}</p>
            <button type="button" className="status-pill" onClick={() => setSelectedComponent(null)}>Close</button>
          </div>
          <p className="text-sm text-slate-300">Status: {selectedComponent.value}</p>
          <p className="text-sm text-slate-300">Role: {selectedComponent.role}</p>
          <pre className="mt-2 rounded border border-cyan-300/15 bg-slate-950/70 p-2 text-xs text-slate-300">{JSON.stringify(selectedComponent.metrics, null, 2)}</pre>
        </GlassCard>
      )}
    </PageShell>
  )
}

export default SystemStatusPage
