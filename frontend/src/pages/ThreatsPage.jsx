import { useEffect, useState } from 'react'
import { ShieldAlert } from 'lucide-react'
import GlassCard from '../components/ui/GlassCard'
import PageShell from '../components/layout/PageShell'
import { getThreats } from '../services/crdsApi'

function ThreatsPage() {
  const [threats, setThreats] = useState([])
  const [selected, setSelected] = useState(null)

  useEffect(() => {
    const load = async () => {
      const data = await getThreats()
      setThreats(data || [])
    }
    load()
    const timer = setInterval(load, 2000)
    return () => clearInterval(timer)
  }, [])

  const colorMap = {
    LOW: 'border-emerald-400/40 bg-emerald-500/10 text-emerald-200',
    MEDIUM: 'border-amber-400/40 bg-amber-500/10 text-amber-200',
    HIGH: 'border-rose-400/40 bg-rose-500/10 text-rose-200',
  }

  const severityBreakdown = threats.reduce((acc, row) => {
    const key = row.threat_level || 'LOW'
    acc[key] = (acc[key] || 0) + 1
    return acc
  }, {})
  const totalThreats = Math.max(1, threats.length)

  return (
    <PageShell title="Dashboard / Threats" icon={<ShieldAlert className="h-3.5 w-3.5" />}>
      <h2 className="mb-4 text-2xl font-semibold tracking-wide text-slate-100">THREAT ANALYSIS</h2>
      <div className="mb-4 grid gap-3 md:grid-cols-2">
        <GlassCard className="border border-cyan-400/20">
          <p className="mb-2 text-xs uppercase tracking-[0.14em] text-cyan-200">Threat severity pie (simulated)</p>
          <div className="flex items-center gap-4">
            <div
              className="h-24 w-24 rounded-full"
              style={{
                background: `conic-gradient(
                  #f43f5e 0 ${((severityBreakdown.HIGH || 0) / totalThreats) * 360}deg,
                  #f59e0b ${((severityBreakdown.HIGH || 0) / totalThreats) * 360}deg ${(((severityBreakdown.HIGH || 0) + (severityBreakdown.MEDIUM || 0)) / totalThreats) * 360}deg,
                  #34d399 ${(((severityBreakdown.HIGH || 0) + (severityBreakdown.MEDIUM || 0)) / totalThreats) * 360}deg 360deg
                )`,
              }}
            />
            <div className="space-y-1 text-xs text-slate-200">
              <p>HIGH: {severityBreakdown.HIGH || 0}</p>
              <p>MEDIUM: {severityBreakdown.MEDIUM || 0}</p>
              <p>LOW: {severityBreakdown.LOW || 0}</p>
            </div>
          </div>
        </GlassCard>
        <GlassCard className="border border-cyan-400/20">
          <p className="mb-2 text-xs uppercase tracking-[0.14em] text-cyan-200">Simulated Threat Intelligence</p>
          <p className="text-sm text-slate-300">Threat actor fields (Source IP, process, origin) are simulated for safe demos.</p>
        </GlassCard>
      </div>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {threats.map((threat) => (
          <GlassCard
            key={threat.id}
            className={`cursor-pointer border ${colorMap[threat.threat_level] || colorMap.MEDIUM} ${threat.threat_level === 'HIGH' ? 'shadow-[0_0_22px_rgba(244,63,94,0.25)]' : ''}`}
            onClick={() => setSelected(threat)}
          >
            <div className="mb-3 flex items-center justify-between">
              <span className="text-xs uppercase tracking-[0.22em]">Threat level</span>
              <span className={`status-pill ${threat.threat_level === 'HIGH' ? 'blocked' : threat.threat_level === 'MEDIUM' ? 'warning' : 'success'}`}>{threat.threat_level}</span>
            </div>
            <p className="mb-1 text-sm text-cyan-100">{threat.threat_type || 'Unclassified threat'}</p>
            <p className="mb-1 text-sm text-slate-100">Confidence: {(Number(threat.confidence_score) * 100).toFixed(1)}%</p>
            <div className="mb-2 h-1.5 rounded bg-slate-900/70">
              <div
                className={`h-full rounded ${threat.threat_level === 'HIGH' ? 'bg-rose-400' : threat.threat_level === 'MEDIUM' ? 'bg-amber-400' : 'bg-emerald-400'}`}
                style={{ width: `${Math.min(100, Math.max(5, Number(threat.confidence_score) * 100))}%` }}
              />
            </div>
            <p className="mb-1 text-xs text-slate-300">{new Date(threat.detected_at).toLocaleString()}</p>
            <p className="text-sm text-slate-200">{threat.message || threat.reason}</p>
          </GlassCard>
        ))}
        {threats.length === 0 && (
          <GlassCard className="border border-cyan-400/20">
            <p className="text-sm text-slate-400">No threats detected yet. Start monitoring and run simulation.</p>
          </GlassCard>
        )}
      </div>
      {selected && (
        <div className="fixed inset-0 z-[80] flex items-center justify-center bg-slate-950/70 p-4" onClick={() => setSelected(null)}>
          <div className="w-full max-w-2xl rounded-2xl border border-cyan-300/30 bg-slate-900/95 p-5 text-slate-100" onClick={(e) => e.stopPropagation()}>
            <div className="mb-3 flex items-center justify-between">
              <h3 className="text-lg font-semibold">Threat Detail</h3>
              <button type="button" className="status-pill" onClick={() => setSelected(null)}>Close</button>
            </div>
            <div className="grid gap-2 text-sm md:grid-cols-2">
              <p><span className="text-cyan-200">Threat Type:</span> {selected.threat_type}</p>
              <p><span className="text-cyan-200">Classification:</span> {selected.threat_type}</p>
              <p><span className="text-cyan-200">Confidence:</span> {(Number(selected.confidence_score) * 100).toFixed(1)}%</p>
              <p><span className="text-cyan-200">Timestamp:</span> {new Date(selected.detected_at).toLocaleString()}</p>
              <p><span className="text-cyan-200">Affected File:</span> {selected.file_path || 'N/A'}</p>
              <p><span className="text-cyan-200">Attack Pattern:</span> {selected.behavior_pattern}</p>
              <p><span className="text-cyan-200">Encryption Type:</span> {selected.encryption_type}</p>
              <p><span className="text-cyan-200">Process:</span> {selected.process_name}</p>
              <p><span className="text-cyan-200">Source IP:</span> {selected.source_ip}</p>
              <p><span className="text-cyan-200">File Origin:</span> {selected.analysis_payload?.file_origin || 'demo_files'}</p>
            </div>
            <div className="mt-4">
              <p className="mb-1 text-xs uppercase tracking-[0.14em] text-cyan-200">Confidence gauge</p>
              <div className="h-3 rounded bg-slate-800">
                <div className="h-full rounded bg-gradient-to-r from-emerald-400 via-amber-400 to-rose-400" style={{ width: `${Math.min(100, Number(selected.confidence_score) * 100)}%` }} />
              </div>
            </div>
          </div>
        </div>
      )}
    </PageShell>
  )
}

export default ThreatsPage
