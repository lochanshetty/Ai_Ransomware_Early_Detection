import { Clock3 } from 'lucide-react'

function PageShell({ title, icon, children }) {
  const now = new Date().toLocaleString()

  return (
    <div className="animate-[pageFade_320ms_ease-out]">
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-2 text-xs text-slate-400">
          {icon ? <span className="text-cyan-400">{icon}</span> : null}
          <span className="uppercase tracking-[0.16em]">{title || 'CRDS Console'}</span>
        </div>
        <div className="flex items-center gap-2 text-xs text-slate-400">
          <Clock3 className="h-3.5 w-3.5 text-slate-500" />
          {now}
        </div>
      </div>
      {children}
    </div>
  )
}

export default PageShell
