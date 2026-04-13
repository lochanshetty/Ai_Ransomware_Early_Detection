import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import AuthLayout from '../components/layout/AuthLayout'

function SignupPage() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const navigate = useNavigate()

  const onSubmit = (event) => {
    event.preventDefault()
    navigate('/app/dashboard')
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
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Full name"
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
          placeholder="Password"
          className="w-full rounded-xl border border-violet-300/30 bg-slate-950/70 px-4 py-3 text-slate-100 outline-none transition focus:border-violet-300 focus:shadow-[0_0_18px_rgba(168,85,247,0.35)]"
          required
        />
        <button
          type="submit"
          className="w-full rounded-xl bg-gradient-to-r from-violet-400 to-cyan-400 px-4 py-3 font-semibold text-slate-950 transition hover:shadow-[0_0_25px_rgba(168,85,247,0.6)]"
        >
          Create Account
        </button>
      </form>
    </AuthLayout>
  )
}

export default SignupPage
