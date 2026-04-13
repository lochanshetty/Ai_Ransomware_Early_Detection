function GlassCard({ children, className = '' }) {
  return (
    <div className={`relative rounded-xl border border-cyan-400/15 bg-[#081226]/70 p-4 shadow-[inset_0_0_0_1px_rgba(59,130,246,0.08),0_0_20px_rgba(6,182,212,0.1)] backdrop-blur-xl transition hover:border-cyan-300/30 ${className}`}>
      <span className="panel-corner" />
      {children}
    </div>
  )
}

export default GlassCard
