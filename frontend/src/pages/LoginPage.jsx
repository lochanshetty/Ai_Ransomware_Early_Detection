import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import AuthLayout from '../components/layout/AuthLayout'
import { login } from '../services/auth'

function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const onSubmit = async (event) => {
    event.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(username, password)
      navigate('/app/dashboard')
    } catch (err) {
      setError(err.message || 'Login failed')
    } finally {
      setLoading(false)
    }
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
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Username"
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
        {error && <p className="text-sm text-rose-300">{error}</p>}
        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-xl bg-gradient-to-r from-cyan-400 to-violet-500 px-4 py-3 font-semibold text-slate-950 transition hover:shadow-[0_0_25px_rgba(56,189,248,0.6)] disabled:opacity-60"
        >
          {loading ? 'Authenticating...' : 'Secure Login'}
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
