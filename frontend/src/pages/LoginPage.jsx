import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import AuthLayout from '../components/layout/AuthLayout'

function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const navigate = useNavigate()

  const onSubmit = (event) => {
    event.preventDefault()
    navigate('/app/dashboard')
  }

  return (
    <AuthLayout
      title="Secure Login"
      subtitle="Authenticate to access the Cognitive Ransomware Defense System."
      altPath="/signup"
      altLabel="Need an account? Create one"
    >
      <form onSubmit={onSubmit} className="space-y-4">
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email address"
          className="w-full rounded-xl border border-cyan-300/30 bg-slate-950/70 px-4 py-3 text-slate-100 outline-none transition focus:border-cyan-300 focus:shadow-[0_0_18px_rgba(34,211,238,0.35)]"
          required
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          className="w-full rounded-xl border border-cyan-300/30 bg-slate-950/70 px-4 py-3 text-slate-100 outline-none transition focus:border-cyan-300 focus:shadow-[0_0_18px_rgba(34,211,238,0.35)]"
          required
        />
        <button
          type="submit"
          className="w-full rounded-xl bg-gradient-to-r from-cyan-400 to-violet-500 px-4 py-3 font-semibold text-slate-950 transition hover:shadow-[0_0_25px_rgba(56,189,248,0.6)]"
        >
          Secure Login
        </button>
      </form>
      <p className="mt-4 text-xs text-slate-500">
        Protected by CRDS anomaly-aware authentication layer.
      </p>
      <Link to="/signup" className="sr-only">
        Signup
      </Link>
    </AuthLayout>
  )
}

export default LoginPage
