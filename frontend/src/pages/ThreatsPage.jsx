import { useEffect, useState } from 'react'
import { ShieldAlert } from 'lucide-react'
import GlassCard from '../components/ui/GlassCard'
import PageShell from '../components/layout/PageShell'
import { getThreats } from '../services/crdsApi'

function ThreatsPage() {
  const [threats, setThreats] = useState([])

  useEffect(() => {
    getThreats().then((data) => setThreats(data || []))
  }, [])

  const colorMap = {
    LOW: 'border-emerald-400/40 bg-emerald-500/10 text-emerald-200',
    MEDIUM: 'border-amber-400/40 bg-amber-500/10 text-amber-200',
    HIGH: 'border-rose-400/40 bg-rose-500/10 text-rose-200',
  }

  return (
    <PageShell title="Dashboard / Threats" icon={<ShieldAlert className="h-3.5 w-3.5" />}>
      <h2 className="mb-4 text-2xl font-semibold tracking-wide text-slate-100">THREAT ANALYSIS</h2>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {threats.map((threat) => (
          <GlassCard key={threat.id} className={`border ${colorMap[threat.threat_level] || colorMap.MEDIUM} ${threat.threat_level === 'HIGH' ? 'shadow-[0_0_22px_rgba(244,63,94,0.25)]' : ''}`}>
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
    </PageShell>
  )
}

export default ThreatsPage
