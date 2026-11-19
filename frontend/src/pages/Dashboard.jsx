import { Link } from 'react-router-dom'
import { Bar, BarChart, CartesianGrid, Cell, Line, LineChart, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { Car, Eye, IndianRupee, ListChecks, Trash2 } from 'lucide-react'
import Spinner from '../components/Spinner.jsx'
import ErrorState from '../components/ErrorState.jsx'
import StatCard from '../components/StatCard.jsx'
import { useToast } from '../components/Toast.jsx'
import useFetch from '../hooks/useFetch.js'
import { api } from '../services/api.js'
import { formatDate, formatINR, formatShort } from '../utils/format.js'

const COLORS = ['#D8312B', '#0F8B8D', '#0E1726', '#F2A516', '#5B6577']

export default function Dashboard() {
  const stats = useFetch(() => api.stats())
  const history = useFetch(() => api.history(50))
  const toast = useToast()

  const remove = async (id) => {
    if (!window.confirm('Delete this prediction?')) return
    try {
      await api.deletePrediction(id)
      toast.success('Prediction deleted')
      stats.reload(); history.reload()
    } catch (e) { toast.error(e.message) }
  }

  if (stats.loading || history.loading) return <Spinner label="Loading dashboard..." />
  if (stats.error || history.error)
    return <div className="px-4 py-16"><ErrorState error={stats.error || history.error} onRetry={() => { stats.reload(); history.reload() }} /></div>

  const s = stats.data
  const items = history.data.items

  if (s.total_predictions === 0) {
    return (
      <section className="mx-auto max-w-xl px-4 py-24 text-center">
        <Car className="mx-auto h-10 w-10 text-steel" />
        <h1 className="mt-4 text-2xl font-bold">No predictions yet</h1>
        <p className="mt-2 text-steel">Make your first estimate and it will show up here.</p>
        <Link to="/predict" className="btn-primary mt-6">Predict a price</Link>
      </section>
    )
  }

  const cats = Object.entries(s.category_counts).map(([name, value]) => ({ name, value }))
  const trend = s.recent_prices.map((p, i) => ({ n: i + 1, price: p.predicted_price }))
  const topBrand = s.top_brands[0]
  const tip = { formatter: (v) => [formatINR(v), 'Price'], contentStyle: { borderRadius: 12, border: '1px solid #D5DBE4' } }

  return (
    <section className="mx-auto max-w-6xl px-4 py-12">
      <h1 className="text-3xl font-bold sm:text-4xl">Dashboard</h1>
      <div className="mt-6 grid gap-4 sm:grid-cols-3">
        <StatCard icon={ListChecks} label="Total predictions" value={s.total_predictions} />
        <StatCard icon={IndianRupee} label="Average predicted price" value={formatShort(s.average_predicted_price)} />
        <StatCard icon={Car} label="Most predicted brand" value={topBrand.brand} hint={`${topBrand.count} predictions`} />
      </div>

      <div className="mt-5 grid gap-5 lg:grid-cols-2">
        <div className="card">
          <h2 className="font-bold">Most predicted brands</h2>
          <div className="mt-4 h-64">
            <ResponsiveContainer>
              <BarChart data={s.top_brands} layout="vertical" margin={{ left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                <XAxis type="number" allowDecimals={false} /><YAxis type="category" dataKey="brand" width={90} />
                <Tooltip /><Bar dataKey="count" fill="#0F8B8D" radius={[0, 6, 6, 0]} name="Predictions" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="card">
          <h2 className="font-bold">Price categories</h2>
          <div className="mt-4 h-64">
            <ResponsiveContainer>
              <PieChart>
                <Pie data={cats} dataKey="value" nameKey="name" innerRadius={55} outerRadius={90} paddingAngle={2} label>
                  {cats.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="card lg:col-span-2">
          <h2 className="font-bold">Latest predicted prices</h2>
          <div className="mt-4 h-64">
            <ResponsiveContainer>
              <LineChart data={trend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="n" label={{ value: 'Prediction (oldest to newest)', position: 'insideBottom', offset: -2 }} />
                <YAxis tickFormatter={(v) => `${(v / 1e5).toFixed(0)}L`} width={50} />
                <Tooltip {...tip} /><Line type="monotone" dataKey="price" stroke="#D8312B" strokeWidth={2.5} dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="card mt-5 overflow-x-auto">
        <h2 className="font-bold">Prediction history</h2>
        <table className="mt-4 w-full min-w-[640px] text-left text-sm">
          <thead className="text-steel"><tr>
            <th className="pb-2 font-medium">Car</th><th className="pb-2 font-medium">Year</th><th className="pb-2 font-medium">Km</th>
            <th className="pb-2 font-medium">Predicted</th><th className="pb-2 font-medium">Date</th><th className="pb-2" />
          </tr></thead>
          <tbody>
            {items.map((r) => (
              <tr key={r.id} className="border-t border-line">
                <td className="py-3 font-medium">{r.brand} {r.model}</td>
                <td>{r.manufacture_year}</td><td>{r.kms_driven.toLocaleString('en-IN')}</td>
                <td>{formatINR(r.predicted_price)}</td><td className="text-steel">{formatDate(r.created_at)}</td>
                <td className="whitespace-nowrap text-right">
                  <Link to={`/result/${r.id}`} aria-label="View" className="mr-2 inline-block p-1 text-steel hover:text-ink"><Eye className="h-4 w-4" /></Link>
                  <button onClick={() => remove(r.id)} aria-label="Delete" className="p-1 text-steel hover:text-signal"><Trash2 className="h-4 w-4" /></button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}
