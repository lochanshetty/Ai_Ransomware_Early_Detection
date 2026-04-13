import { Component } from 'react'

class AppErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, message: '' }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, message: error?.message || 'Unknown runtime error' }
  }

  componentDidCatch(error) {
    console.error('CRDS frontend runtime error:', error)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-[#020617] px-6 py-10 text-slate-100">
          <h1 className="text-2xl font-semibold text-rose-300">CRDS UI failed to render</h1>
          <p className="mt-3 text-sm text-slate-300">
            Refresh the page once. If the issue persists, restart Django and clear browser cache.
          </p>
          <pre className="mt-4 overflow-auto rounded-lg border border-rose-400/30 bg-rose-500/10 p-3 text-xs text-rose-200">
            {this.state.message}
          </pre>
        </div>
      )
    }

    return this.props.children
  }
}

export default AppErrorBoundary
