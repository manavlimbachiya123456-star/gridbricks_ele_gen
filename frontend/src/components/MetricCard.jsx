export default function MetricCard({ label, value, unit, accent = 'cyan' }) {
  const colors = { cyan: 'text-cyan-300', emerald: 'text-emerald-300', violet: 'text-violet-300', amber: 'text-amber-300' }
  const dots = { cyan: 'bg-cyan-300', emerald: 'bg-emerald-300', violet: 'bg-violet-300', amber: 'bg-amber-300' }
  return <div className="group rounded-2xl border border-slate-700/70 bg-slate-900/70 p-5 shadow-xl shadow-black/10 transition duration-200 hover:-translate-y-0.5 hover:border-slate-600 hover:bg-slate-900">
    <div className="flex items-center justify-between"><p className="text-xs font-semibold uppercase tracking-[0.15em] text-slate-400">{label}</p><span className={`h-2 w-2 rounded-full ${dots[accent] || dots.cyan} opacity-70`} /></div>
    <p className={`mt-3 text-3xl font-bold ${colors[accent] || colors.cyan}`}>{value ?? '—'}<span className="ml-1 text-sm font-medium text-slate-400">{unit}</span></p>
  </div>
}

