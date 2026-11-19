import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, Info, RotateCcw } from 'lucide-react'
import Spinner from '../components/Spinner.jsx'
import ErrorState from '../components/ErrorState.jsx'
import useFetch from '../hooks/useFetch.js'
import { api } from '../services/api.js'
import { formatDate, formatINR, formatNumber, formatShort } from '../utils/format.js'

const CATEGORY_TEXT = {
  Budget: 'Under ₹3 lakh', Economy: '₹3-6 lakh', 'Mid-range': '₹6-12 lakh',
  Premium: '₹12-30 lakh', Luxury: 'Above ₹30 lakh',
}

export default function Result() {
  const { id } = useParams()
  const { data: r, error, loading, reload } = useFetch(() => api.prediction(id), [id])

  if (loading) return <Spinner label="Loading estimate..." />
  if (error) return <div className="px-4 py-16"><ErrorState error={error} onRetry={reload} /></div>

  const owner = r.ownership === 0 ? 'Unregistered' : `Owner #${r.ownership}`
  const details = [
    ['Car', `${r.brand} ${r.model}`], ['Year', r.manufacture_year], ['Driven', `${formatNumber(r.kms_driven)} km`],
    ['Fuel', r.fuel_type], ['Transmission', r.transmission], ['Ownership', owner],
    ['Engine', `${formatNumber(r.engine_cc)} cc`], ['Seats', r.seats],
  ]
  // Position of the estimate inside the low-high band, for the range bar.
  const pos = ((r.predicted_price - r.price_low) / (r.price_high - r.price_low)) * 100

  return (
    <section className="mx-auto max-w-4xl px-4 py-12">
      <Link to="/predict" className="inline-flex items-center gap-1 text-sm text-steel hover:text-ink"><ArrowLeft className="h-4 w-4" /> New estimate</Link>
      <div className="mt-4 grid gap-5 md:grid-cols-5">
        <div className="card md:col-span-3">
          <p className="text-sm text-steel">Estimated selling price</p>
          <p className="mt-1 font-display text-5xl font-extrabold sm:text-6xl">{formatINR(r.predicted_price)}</p>
          <p className="mt-1 text-steel">about {formatShort(r.predicted_price)}</p>

          <div className="mt-8">
            <div className="relative h-2 rounded-full bg-paper">
              <div className="absolute inset-y-0 rounded-full bg-teal/30" style={{ left: 0, right: 0 }} />
              <div className="absolute top-1/2 h-4 w-4 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-white bg-signal shadow"
                style={{ left: `${Math.min(Math.max(pos, 2), 98)}%` }} />
            </div>
            <div className="mt-2 flex justify-between text-sm">
              <span>{formatShort(r.price_low)}</span><span>{formatShort(r.price_high)}</span>
            </div>
            <p className="mt-1 text-xs text-steel">Typical range: the middle 80% of errors the model made on cars it had not seen.</p>
          </div>
        </div>

        <div className="card md:col-span-2">
          <p className="text-sm text-steel">Price category</p>
          <p className="mt-1 font-display text-3xl font-extrabold text-teal">{r.price_category}</p>
          <p className="text-sm text-steel">{CATEGORY_TEXT[r.price_category]}</p>
          <p className="mt-5 text-sm">
            A {r.manufacture_year} {r.brand} {r.model} with {formatNumber(r.kms_driven)} km, {r.fuel_type.toLowerCase()} and
            {' '}{r.transmission.toLowerCase()}, is estimated at {formatShort(r.predicted_price)}.
          </p>
          <p className="mt-3 text-xs text-steel">Saved {formatDate(r.created_at)}</p>
        </div>
      </div>

      <div className="card mt-5">
        <h2 className="text-lg font-bold">Car details used</h2>
        <dl className="mt-4 grid grid-cols-2 gap-4 sm:grid-cols-4">
          {details.map(([k, v]) => (<div key={k}><dt className="text-xs text-steel">{k}</dt><dd className="font-medium">{v}</dd></div>))}
        </dl>
      </div>

      <div className="mt-5 flex items-start gap-2 rounded-xl border border-amber/60 bg-amber/10 p-4 text-sm">
        <Info className="mt-0.5 h-4 w-4 shrink-0" />
        <p>{r.disclaimer} Real prices also depend on condition, service history, location and negotiation.</p>
      </div>

      <div className="mt-6 flex flex-wrap gap-3">
        <Link to="/predict" className="btn-primary"><RotateCcw className="h-4 w-4" /> Make another prediction</Link>
        <Link to="/dashboard" className="btn-ghost">View dashboard</Link>
      </div>
    </section>
  )
}
