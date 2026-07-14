import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import AuthLayout from '../components/layout/AuthLayout'
import { login, register } from '../services/auth'

function SignupPage() {
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const onSubmit = async (event) => {
    event.preventDefault()
    setError('')
    setLoading(true)
    try {
      await register(username, email, password)
      await login(username, password)
      navigate('/app/dashboard')
    } catch (err) {
      setError(err.message || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthLayout
      title="Create Account"
      subtitle="Provision your operator identity for the CRDS control center."
      altPath="/login"
      altLabel="Already registered? Secure login"
    >
      <form onSubmit={onSubmit} className="space-y-4">
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Username"
          className="w-full rounded-xl border border-violet-300/30 bg-slate-950/70 px-4 py-3 text-slate-100 outline-none transition focus:border-violet-300 focus:shadow-[0_0_18px_rgba(168,85,247,0.35)]"
          required
        />
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email address"
          className="w-full rounded-xl border border-violet-300/30 bg-slate-950/70 px-4 py-3 text-slate-100 outline-none transition focus:border-violet-300 focus:shadow-[0_0_18px_rgba(168,85,247,0.35)]"
          required
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password (min 8 characters)"
          className="w-full rounded-xl border border-violet-300/30 bg-slate-950/70 px-4 py-3 text-slate-100 outline-none transition focus:border-violet-300 focus:shadow-[0_0_18px_rgba(168,85,247,0.35)]"
          required
          minLength={8}
        />
        {error && <p className="text-sm text-rose-300">{error}</p>}
        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-xl bg-gradient-to-r from-violet-400 to-cyan-400 px-4 py-3 font-semibold text-slate-950 transition hover:shadow-[0_0_25px_rgba(168,85,247,0.6)] disabled:opacity-60"
        >
          {loading ? 'Creating account...' : 'Create Account'}
        </button>
      </form>
    </AuthLayout>
  )
}

export default SignupPage
