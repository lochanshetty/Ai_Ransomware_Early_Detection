import { useEffect, useState } from 'react'
import { Activity, AlertTriangle, CheckCircle2 } from 'lucide-react'
import { getHealth } from '../../services/crdsApi'

function StartupDiagnostics() {
  const [health, setHealth] = useState(null)
  const [visible, setVisible] = useState(true)

  useEffect(() => {
    getHealth().then((payload) => setHealth(payload))
  }, [])

  if (!visible) return null

  const healthy = health?.status === 'ok'
  return (
    <div className={`fixed bottom-4 right-4 z-[100] w-[320px] rounded-xl border p-3 shadow-xl backdrop-blur-xl ${
      healthy ? 'border-emerald-400/30 bg-emerald-500/10' : 'border-rose-400/30 bg-rose-500/10'
    }`}>
      <div className="mb-2 flex items-center justify-between">
        <div className="flex items-center gap-2 text-sm">
          {healthy ? <CheckCircle2 className="h-4 w-4 text-emerald-300" /> : <AlertTriangle className="h-4 w-4 text-rose-300" />}
          <span className="font-medium">{healthy ? 'Backend connected' : 'Backend unavailable'}</span>
        </div>
        <button type="button" onClick={() => setVisible(false)} className="text-xs text-slate-400 hover:text-slate-200">Dismiss</button>
      </div>
      <div className="space-y-1 text-xs text-slate-200">
        <p className="flex items-center gap-1"><Activity className="h-3.5 w-3.5" /> {health?.service || 'CRDS backend'}</p>
        <p>Logs: {health?.counts?.logs ?? 0} | Threats: {health?.counts?.threats ?? 0} | Alerts: {health?.counts?.alerts ?? 0}</p>
      </div>
    </div>
  )
}

export default StartupDiagnostics
