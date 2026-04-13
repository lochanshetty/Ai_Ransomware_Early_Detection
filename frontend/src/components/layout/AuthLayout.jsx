import { Shield } from 'lucide-react'
import { Link } from 'react-router-dom'

function AuthLayout({ title, subtitle, altPath, altLabel, children }) {
  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-[#030712] px-4">
      <div className="cyber-grid pointer-events-none absolute inset-0 opacity-40" />
      <div className="pointer-events-none absolute -left-20 top-20 h-64 w-64 rounded-full bg-cyan-500/20 blur-3xl" />
      <div className="pointer-events-none absolute -right-20 bottom-10 h-64 w-64 rounded-full bg-fuchsia-500/20 blur-3xl" />

      <div className="w-full max-w-md rounded-3xl border border-cyan-300/20 bg-slate-900/40 p-8 backdrop-blur-2xl shadow-[0_0_35px_rgba(34,211,238,0.2)]">
        <div className="mb-6 flex items-center gap-3 text-cyan-300">
          <Shield className="h-7 w-7" />
          <h1 className="text-2xl font-semibold">{title}</h1>
        </div>
        <p className="mb-6 text-sm text-slate-300">{subtitle}</p>
        {children}
        <div className="mt-5 text-sm text-slate-400">
          <Link to={altPath} className="text-cyan-300 transition hover:text-cyan-200">
            {altLabel}
          </Link>
        </div>
      </div>
    </div>
  )
}

export default AuthLayout
