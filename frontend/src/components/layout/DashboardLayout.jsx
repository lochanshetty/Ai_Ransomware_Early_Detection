import { createElement } from 'react'
import {
  Activity,
  FileText,
  LayoutDashboard,
  Lock,
  ShieldAlert,
  Siren,
} from 'lucide-react'
import { NavLink } from 'react-router-dom'
import LiveDot from '../ui/LiveDot'

const navItems = [
  { to: '/app/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/app/logs', label: 'Logs', icon: FileText },
  { to: '/app/threats', label: 'Threats', icon: ShieldAlert },
  { to: '/app/honeypots', label: 'Honeypots', icon: Lock },
  { to: '/app/status', label: 'System Status', icon: Activity },
]

function DashboardLayout({ children }) {
  return (
    <div className="relative min-h-screen bg-[#020617] text-slate-100">
      <div className="cyber-grid pointer-events-none absolute inset-0 opacity-20" />
      <div className="pointer-events-none absolute right-20 top-20 h-72 w-72 rounded-full bg-violet-500/20 blur-3xl" />

      <div className="relative z-10 grid min-h-screen grid-cols-1 lg:grid-cols-[280px_1fr]">
        <aside className="relative border-r border-cyan-400/15 bg-[#071225]/80 backdrop-blur-xl">
          <div className="flex items-center gap-3 border-b border-cyan-400/15 px-6 py-5">
            <Siren className="h-7 w-7 text-cyan-300" />
            <div>
              <p className="font-semibold tracking-wide">CRDS</p>
              <div className="flex items-center gap-2 text-xs text-emerald-300">
                <LiveDot />
                Live Monitoring
              </div>
            </div>
          </div>
          <nav className="p-3">
            {navItems.map(({ to, label, icon }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  `mb-1.5 flex items-center gap-3 rounded-xl px-4 py-2.5 text-sm transition ${
                    isActive
                      ? 'bg-cyan-500/15 text-cyan-200 shadow-[inset_0_0_0_1px_rgba(34,211,238,0.25)]'
                      : 'text-slate-300 hover:bg-slate-800/80 hover:text-cyan-200'
                  }`
                }
              >
                {createElement(icon, { className: 'h-4 w-4' })}
                {label}
              </NavLink>
            ))}
          </nav>
          <div className="absolute bottom-4 left-4 right-4 rounded-lg border border-slate-700/60 bg-slate-900/60 px-3 py-2 text-xs text-slate-500">
            Logout
          </div>
        </aside>

        <main className="p-6 md:p-8">{children}</main>
      </div>
    </div>
  )
}

export default DashboardLayout
