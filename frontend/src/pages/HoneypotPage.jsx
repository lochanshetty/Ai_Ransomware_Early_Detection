import { useEffect, useState } from 'react'
import { Bug, Lock, MapPin, Signal } from 'lucide-react'
import GlassCard from '../components/ui/GlassCard'
import PageShell from '../components/layout/PageShell'
import { generateHoneypots, getHoneypotStatus, getHoneypotTriggered } from '../services/crdsApi'

function HoneypotPage() {
  const [status, setStatus] = useState(null)
  const [triggered, setTriggered] = useState([])

  const loadStatus = async () => {
    const [statusData, triggeredData] = await Promise.all([
      getHoneypotStatus(),
      getHoneypotTriggered(),
    ])
    setStatus(statusData)
    setTriggered(triggeredData)
  }

  useEffect(() => {
    let mounted = true
    const loadOnMount = async () => {
      const [statusData, triggeredData] = await Promise.all([
        getHoneypotStatus(),
        getHoneypotTriggered(),
      ])
      if (!mounted) return
      setStatus(statusData)
      setTriggered(triggeredData)
    }
    loadOnMount()
    return () => {
      mounted = false
    }
  }, [])

  const createHoneypots = async () => {
    await generateHoneypots()
    await loadStatus()
  }

  return (
    <PageShell title="Dashboard / Honeypots" icon={<Lock className="h-3.5 w-3.5" />}>
      <h2 className="mb-4 text-2xl font-semibold tracking-wide text-slate-100">HONEYPOTS</h2>
      <GlassCard className="mb-4">
        <div className="mb-4 flex flex-wrap gap-2">
          <button
            type="button"
            className="rounded-xl bg-gradient-to-r from-cyan-400 to-violet-500 px-4 py-2 font-medium text-slate-950 transition hover:shadow-[0_0_20px_rgba(34,211,238,0.5)]"
            onClick={createHoneypots}
          >
            Create Honeypots
          </button>
          <button
            type="button"
            className="rounded-xl border border-cyan-300/30 bg-slate-950/60 px-4 py-2 text-cyan-100 transition hover:border-cyan-200"
            onClick={loadStatus}
          >
            Refresh Status
          </button>
        </div>
        {status && (
          <div className="mb-4 rounded-xl border border-cyan-300/20 bg-slate-950/60 p-4 text-sm text-slate-200">
            Total: {status.total_files} | Triggered: {status.triggered_files} | Safe: {status.safe_files}
          </div>
        )}
      </GlassCard>
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {(triggered.length ? triggered : [{ id: 'h-001', file_path: 'H-001 SSH Trap Alpha' }, { id: 'h-002', file_path: 'H-002 HTTP Decoy Beta' }, { id: 'h-003', file_path: 'H-003 SMB Lure Gamma' }]).map((item, idx) => (
          <GlassCard key={item.id} className={`min-h-[160px] ${idx === 2 ? 'border-rose-400/40 shadow-[0_0_24px_rgba(244,63,94,0.25)]' : ''}`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-cyan-300"><Bug className="h-4 w-4" /><p className="font-semibold">H-{String(idx + 1).padStart(3, '0')}</p></div>
              <span className={`h-2 w-2 rounded-full ${idx === 2 ? 'bg-rose-400' : 'bg-cyan-300'}`} />
            </div>
            <p className="mt-2 text-sm text-slate-200">{item.file_path}</p>
            <span className={`status-pill ${idx === 2 ? 'blocked' : 'success'} mt-2 inline-block`}>{idx === 2 ? 'ALERT' : 'ACTIVE'}</span>
            <div className="mt-3 flex items-center justify-between text-xs text-slate-400">
              <span className="flex items-center gap-1"><MapPin className="h-3 w-3" /> Internal-{String.fromCharCode(65 + idx)}</span>
              <span className="flex items-center gap-1"><Signal className="h-3 w-3" /> {12 + idx * 7} triggers</span>
            </div>
          </GlassCard>
        ))}
      </div>
    </PageShell>
  )
}

export default HoneypotPage
