import { useEffect, useMemo, useState } from 'react'
import { FileText, Search } from 'lucide-react'
import GlassCard from '../components/ui/GlassCard'
import PageShell from '../components/layout/PageShell'
import { getMonitorLogs, openFilePath } from '../services/crdsApi'

function LogsPage() {
  const [logs, setLogs] = useState([])
  const [search, setSearch] = useState('')
  const [filter, setFilter] = useState('all')

  const loadLogs = async (activeFilter = filter) => {
    const data = await getMonitorLogs(activeFilter)
    setLogs(data || [])
  }

  useEffect(() => {
    loadLogs('all')
    const timer = setInterval(() => loadLogs(filter), 2000)
    return () => clearInterval(timer)
  }, [filter])

  const filtered = useMemo(() => {
    return logs.filter((log) => {
      const status = log.status || (log.action === 'rename' ? 'alert' : log.action === 'modify' ? 'warning' : 'success')
      const matchSearch = `${log.event_type} ${log.file_path} ${log.action}`.toLowerCase().includes(search.toLowerCase())
      const matchFilter = filter === 'all' ? true : status === filter
      return matchSearch && matchFilter
    })
  }, [logs, search, filter])

  const distribution = useMemo(() => {
    const base = { success: 0, warning: 0, alert: 0, blocked: 0 }
    for (const row of filtered) {
      const key = row.status || (row.action === 'rename' ? 'alert' : row.action === 'modify' ? 'warning' : 'success')
      if (base[key] !== undefined) base[key] += 1
    }
    return base
  }, [filtered])

  const timelineBuckets = useMemo(() => {
    const buckets = Array.from({ length: 8 }, (_, idx) => ({ label: `${8 - idx}`, count: 0 }))
    const now = Date.now()
    for (const row of filtered) {
      const ts = new Date(row.timestamp).getTime()
      const ageSec = Math.max(0, Math.floor((now - ts) / 1000))
      const idx = Math.min(7, Math.floor(ageSec / 15))
      buckets[7 - idx].count += 1
    }
    return buckets
  }, [filtered])

  const mapChipClass = (chip) => {
    const lowered = chip.toLowerCase()
    if (lowered === 'blocked') return 'status-pill blocked'
    if (lowered === 'alert') return 'status-pill alert'
    if (lowered === 'success') return 'status-pill success'
    if (lowered === 'warning') return 'status-pill warning'
    return 'status-pill'
  }

  const handleOpenLogFile = async (log) => {
    if (!log.file_path) return
    const previewUrl = await openFilePath(log.file_path)
    window.open(previewUrl, '_blank', 'noopener,noreferrer')
  }

  return (
    <PageShell title="Dashboard / Logs" icon={<FileText className="h-3.5 w-3.5" />}>
      <GlassCard>
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <h2 className="text-2xl font-semibold tracking-wide text-slate-100">SYSTEM LOGS</h2>
          <div className="flex gap-2">
            <div className="relative">
              <Search className="pointer-events-none absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search event/file/process"
                className="rounded-lg border border-cyan-300/20 bg-slate-950/70 py-2 pl-9 pr-3 text-sm text-slate-100 outline-none focus:border-cyan-300"
              />
            </div>
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="rounded-lg border border-cyan-300/20 bg-slate-950/70 px-3 py-2 text-sm text-slate-100 outline-none"
            >
              <option value="all">All</option>
              <option value="success">Success</option>
              <option value="warning">Warning</option>
              <option value="alert">Alert</option>
              <option value="blocked">Blocked</option>
            </select>
          </div>
        </div>
        <div className="mb-3 flex gap-2 text-xs">
          {['ALL', 'BLOCKED', 'ALERT', 'SUCCESS', 'WARNING'].map((chip) => (
            <span key={chip} className={mapChipClass(chip)}>{chip}</span>
          ))}
        </div>
        <div className="mb-4 grid gap-3 md:grid-cols-2">
          <div className="rounded-xl border border-cyan-300/15 p-3">
            <p className="mb-2 text-xs uppercase tracking-[0.14em] text-cyan-200">Logs per type</p>
            {Object.entries(distribution).map(([key, value]) => (
              <div key={key} className="mb-2">
                <div className="mb-1 flex justify-between text-xs text-slate-300">
                  <span>{key.toUpperCase()}</span><span>{value}</span>
                </div>
                <div className="h-2 rounded bg-slate-800/80">
                  <div className="h-full rounded bg-cyan-400" style={{ width: `${Math.min(100, value * 10)}%` }} />
                </div>
              </div>
            ))}
          </div>
          <div className="rounded-xl border border-cyan-300/15 p-3">
            <p className="mb-2 text-xs uppercase tracking-[0.14em] text-cyan-200">Timeline activity</p>
            <div className="flex h-24 items-end gap-2">
              {timelineBuckets.map((bucket) => (
                <div key={bucket.label} className="flex-1 text-center">
                  <div
                    className="mx-auto w-full rounded-t bg-violet-400/80"
                    style={{ height: `${Math.max(8, bucket.count * 12)}px` }}
                    title={`${bucket.count} logs`}
                  />
                  <p className="mt-1 text-[10px] text-slate-400">-{bucket.label * 15}s</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="max-h-[60vh] overflow-auto rounded-xl border border-cyan-300/15">
          <table className="min-w-full text-left text-sm">
            <thead className="bg-slate-800/60 text-cyan-100">
              <tr>
                <th className="px-4 py-3 text-[11px] tracking-[0.12em]">Timestamp</th>
                <th className="px-4 py-3 text-[11px] tracking-[0.12em]">Event Type</th>
                <th className="px-4 py-3 text-[11px] tracking-[0.12em]">File / Process</th>
                <th className="px-4 py-3 text-[11px] tracking-[0.12em]">Status</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((log) => {
                const status = log.status || (log.action === 'rename' ? 'alert' : log.action === 'modify' ? 'warning' : 'success')
                return (
                <tr
                  key={log.id}
                  className="cursor-pointer border-t border-cyan-300/10 text-slate-200 hover:bg-slate-800/35"
                  onClick={() => handleOpenLogFile(log)}
                >
                  <td className="px-4 py-3.5 text-[12px]">{new Date(log.timestamp).toLocaleString()}</td>
                  <td className="px-4 py-3.5 font-medium">{(log.action || log.event_type).replace('_', ' ')}</td>
                  <td className="px-4 py-3.5 text-slate-400">{log.file_path || '-'}</td>
                  <td className="px-4 py-3.5">
                    <span className={mapChipClass(status.toUpperCase())}>
                      {status.toUpperCase()}
                    </span>
                  </td>
                </tr>
                )
              })}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan="4" className="px-4 py-8 text-center text-slate-400">No logs available.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </GlassCard>
    </PageShell>
  )
}

export default LogsPage
