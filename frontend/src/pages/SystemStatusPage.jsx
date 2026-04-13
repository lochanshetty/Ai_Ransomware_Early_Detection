import { createElement } from 'react'
import { useEffect, useState } from 'react'
import { Activity, Cpu, Database, HardDrive, Radar, Shield, Wifi } from 'lucide-react'
import GlassCard from '../components/ui/GlassCard'
import PageShell from '../components/layout/PageShell'
import { getMonitorStatus } from '../services/crdsApi'

function SystemStatusPage() {
  const [status, setStatus] = useState(null)

  useEffect(() => {
    getMonitorStatus().then((data) => setStatus(data))
  }, [])

  const telemetry = [
    { label: 'Firewall', value: 'Operational', icon: Shield },
    { label: 'IDS/IPS', value: 'Operational', icon: Radar },
    { label: 'Threat DB', value: 'Operational', icon: Database },
    { label: 'ML Engine', value: status?.is_running ? 'Operational' : 'Offline', icon: Cpu },
    { label: 'Network Monitor', value: 'Operational', icon: Wifi },
    { label: 'Storage', value: 'Degraded', icon: HardDrive },
  ]

  return (
    <PageShell title="Dashboard / System Status" icon={<Activity className="h-3.5 w-3.5" />}>
      <h2 className="mb-4 text-2xl font-semibold tracking-wide text-slate-100">SYSTEM STATUS</h2>
      <GlassCard className="mb-4 border-cyan-500/30">
        <p className="text-xl font-semibold text-cyan-300">ALL SYSTEMS OPERATIONAL</p>
        <p className="mt-1 text-xs text-slate-400">Uptime: 99.97% | Last scan: {new Date().toLocaleString()}</p>
      </GlassCard>
      <div className="grid gap-3 md:grid-cols-3">
        {telemetry.map(({ label, value, icon }) => (
          <GlassCard key={label}>
            <div className="mb-2 flex items-center justify-between gap-2 text-cyan-200">
              <div className="flex items-center gap-2">
              {createElement(icon, { className: 'h-5 w-5' })}
              <p className="text-sm">{label}</p>
              </div>
              <span className={`status-pill ${value === 'Degraded' ? 'warning' : 'success'}`}>{value.toUpperCase()}</span>
            </div>
          </GlassCard>
        ))}
      </div>
      <div className="mt-3 grid gap-3 md:grid-cols-3">
        <GlassCard>
          <p className="text-xs text-cyan-300">CPU</p>
          <p className="text-4xl font-bold text-cyan-300">34%</p>
          <div className="mt-2 h-2 rounded bg-slate-800"><div className="h-full w-1/3 rounded bg-gradient-to-r from-cyan-400 to-blue-500" /></div>
        </GlassCard>
        <GlassCard>
          <p className="text-xs text-emerald-300">MEMORY</p>
          <p className="text-4xl font-bold text-emerald-300">62%</p>
          <div className="mt-2 h-2 rounded bg-slate-800"><div className="h-full w-3/5 rounded bg-gradient-to-r from-emerald-400 to-green-500" /></div>
        </GlassCard>
        <GlassCard>
          <p className="text-xs text-violet-300">NETWORK</p>
          <p className="text-4xl font-bold text-violet-300">2.4 GB/S</p>
          <p className="mt-2 text-xs text-slate-400">Current throughput</p>
        </GlassCard>
      </div>
    </PageShell>
  )
}

export default SystemStatusPage
