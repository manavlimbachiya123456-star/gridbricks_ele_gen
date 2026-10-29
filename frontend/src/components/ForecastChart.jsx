import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts'
export default function ForecastChart({ rows }) {
  const data = rows.filter(r => r.forecast != null || r.actual != null).map(r => ({ ...r, label: new Date(r.start_time).toLocaleDateString(undefined, { day: '2-digit', hour: '2-digit' }) }))
  return <div className="h-[360px] w-full"><ResponsiveContainer>
    <LineChart data={data} margin={{ top: 10, right: 18, left: 0, bottom: 0 }}><CartesianGrid stroke="#24364b" strokeDasharray="3 3" />
      <XAxis dataKey="label" tick={{ fill: '#94a3b8', fontSize: 11 }} minTickGap={28} /><YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} unit=" MW" />
      <Tooltip contentStyle={{ background: '#0f1d2d', border: '1px solid #29425b', borderRadius: 12 }} /><Legend />
      <Line type="monotone" dataKey="actual" name="Actual" stroke="#34d399" strokeWidth={2} dot={false} connectNulls={false} />
      <Line type="monotone" dataKey="forecast" name="Forecast" stroke="#38bdf8" strokeWidth={2} dot={false} connectNulls={false} />
    </LineChart>
  </ResponsiveContainer></div>
}

