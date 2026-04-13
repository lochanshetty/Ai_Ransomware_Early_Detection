import { useEffect, useMemo, useState } from 'react'
import { FileText, Search } from 'lucide-react'
import GlassCard from '../components/ui/GlassCard'
import PageShell from '../components/layout/PageShell'
import { getMonitorLogs } from '../services/crdsApi'

function LogsPage() {
  const [logs, setLogs] = useState([])
  const [search, setSearch] = useState('')
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    getMonitorLogs().then((data) => setLogs(data || []))
  }, [])

  const filtered = useMemo(() => {
    return logs.filter((log) => {
      const status = log.action === 'rename' ? 'alert' : log.action === 'modify' ? 'suspicious' : 'monitoring'
      const matchSearch = `${log.event_type} ${log.file_path} ${log.action}`.toLowerCase().includes(search.toLowerCase())
      const matchFilter = filter === 'all' ? true : status === filter
      return matchSearch && matchFilter
    })
  }, [logs, search, filter])

  const mapChipClass = (chip) => {
    const lowered = chip.toLowerCase()
    if (lowered === 'blocked') return 'status-pill blocked'
    if (lowered === 'alert') return 'status-pill alert'
    if (lowered === 'success') return 'status-pill success'
    if (lowered === 'warning') return 'status-pill warning'
    return 'status-pill'
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
              <option value="monitoring">Monitoring</option>
              <option value="suspicious">Suspicious</option>
              <option value="alert">Alert</option>
            </select>
          </div>
        </div>
        <div className="mb-3 flex gap-2 text-xs">
          {['ALL', 'BLOCKED', 'ALERT', 'SUCCESS', 'WARNING'].map((chip) => (
            <span key={chip} className={mapChipClass(chip)}>{chip}</span>
          ))}
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
                const status = log.action === 'rename' ? 'alert' : log.action === 'modify' ? 'suspicious' : 'monitoring'
                return (
                <tr key={log.id} className="border-t border-cyan-300/10 text-slate-200 hover:bg-slate-800/35">
                  <td className="px-4 py-3.5 text-[12px]">{new Date(log.timestamp).toLocaleString()}</td>
                  <td className="px-4 py-3.5 font-medium">{(log.action || log.event_type).replace('_', ' ')}</td>
                  <td className="px-4 py-3.5 text-slate-400">{log.file_path || '-'}</td>
                  <td className="px-4 py-3.5">
                    <span className={mapChipClass(status === 'monitoring' ? 'SUCCESS' : status === 'suspicious' ? 'WARNING' : 'BLOCKED')}>
                      {status === 'monitoring' ? 'SUCCESS' : status === 'suspicious' ? 'WARNING' : 'BLOCKED'}
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
