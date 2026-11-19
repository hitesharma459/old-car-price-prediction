import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Loader2, Sparkles } from 'lucide-react'
import Spinner from '../components/Spinner.jsx'
import ErrorState from '../components/ErrorState.jsx'
import { useToast } from '../components/Toast.jsx'
import useFetch from '../hooks/useFetch.js'
import { api } from '../services/api.js'

const EMPTY = { brand: '', model: '', manufacture_year: '', kms_driven: '', fuel_type: '',
  transmission: '', ownership: '', engine_cc: '', seats: '' }

function Field({ label, error, children }) {
  return (
    <div>
      <label className="field-label">{label}</label>
      {children}
      {error && <p className="mt-1 text-xs text-signal" role="alert">{error}</p>}
    </div>
  )
}

export default function Predict() {
  const { data: opts, error, loading, reload } = useFetch(() => api.options())
  const [form, setForm] = useState(EMPTY)
  const [errors, setErrors] = useState({})
  const [submitting, setSubmitting] = useState(false)
  const navigate = useNavigate()
  const toast = useToast()

  const models = useMemo(() => (opts && form.brand ? opts.brands[form.brand] || [] : []), [opts, form.brand])
  const selectedModel = models.find((m) => m.name === form.model)
  const years = useMemo(() => {
    if (!opts) return []
    const [lo, hi] = opts.year_range
    return Array.from({ length: hi - lo + 1 }, (_, i) => hi - i)
  }, [opts])

  if (loading) return <Spinner label="Loading car options..." />
  if (error) return <div className="px-4 py-16"><ErrorState error={error} onRetry={reload} /></div>

  const set = (key, value) => {
    setForm((f) => ({ ...f, [key]: value }))
    setErrors((e) => ({ ...e, [key]: undefined }))
  }

  const pickBrand = (brand) => setForm({ ...form, brand, model: '', fuel_type: '', transmission: '', engine_cc: '', seats: '' })

  // Selecting a model pre-fills engine size and seats with the typical values from the data.
  const pickModel = (name) => {
    const m = models.find((x) => x.name === name)
    setForm((f) => ({
      ...f, model: name,
      engine_cc: m ? String(m.median_engine_cc) : '',
      seats: m ? String(m.typical_seats) : '',
      fuel_type: m && m.fuel_types.length === 1 ? m.fuel_types[0] : '',
      transmission: m && m.transmissions.length === 1 ? m.transmissions[0] : '',
    }))
    setErrors((e) => ({ ...e, model: undefined }))
  }

  const validate = () => {
    const e = {}
    const req = ['brand', 'model', 'fuel_type', 'transmission', 'ownership', 'seats', 'manufacture_year']
    req.forEach((k) => { if (form[k] === '') e[k] = 'Required' })
    const km = Number(form.kms_driven)
    if (form.kms_driven === '' || Number.isNaN(km) || km < 0) e.kms_driven = 'Enter kilometres driven (0 or more)'
    else if (km > opts.kms_range[1]) e.kms_driven = `Max supported is ${opts.kms_range[1].toLocaleString('en-IN')} km`
    const cc = Number(form.engine_cc)
    if (!cc || cc < opts.engine_range[0] || cc > opts.engine_range[1])
      e.engine_cc = `Enter ${opts.engine_range[0]}-${opts.engine_range[1]} cc`
    setErrors(e)
    return Object.keys(e).length === 0
  }

  const submit = async (ev) => {
    ev.preventDefault()
    if (!validate()) { toast.error('Please fix the highlighted fields.'); return }
    setSubmitting(true)
    try {
      const payload = {
        brand: form.brand, model: form.model, fuel_type: form.fuel_type, transmission: form.transmission,
        manufacture_year: Number(form.manufacture_year), kms_driven: Number(form.kms_driven),
        ownership: Number(form.ownership), engine_cc: Number(form.engine_cc), seats: Number(form.seats),
      }
      const result = await api.predict(payload)
      toast.success('Estimate ready')
      navigate(`/result/${result.id}`)
    } catch (err) {
      toast.error(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  const fuels = selectedModel?.fuel_types || opts.fuel_types
  const trans = selectedModel?.transmissions || opts.transmissions
  const cls = (k) => `input ${errors[k] ? 'input-error' : ''}`

  return (
    <section className="mx-auto max-w-3xl px-4 py-12">
      <h1 className="text-3xl font-bold sm:text-4xl">Estimate your car's price</h1>
      <p className="mt-2 text-steel">Every option below comes from the dataset the model was trained on.</p>

      <form onSubmit={submit} noValidate className="card mt-8 grid gap-5 sm:grid-cols-2">
        <Field label="Brand" error={errors.brand}>
          <select className={cls('brand')} value={form.brand} onChange={(e) => pickBrand(e.target.value)}>
            <option value="">Select brand</option>
            {Object.keys(opts.brands).map((b) => <option key={b}>{b}</option>)}
          </select>
        </Field>
        <Field label="Model" error={errors.model}>
          <select className={cls('model')} value={form.model} disabled={!form.brand} onChange={(e) => pickModel(e.target.value)}>
            <option value="">{form.brand ? 'Select model' : 'Choose a brand first'}</option>
            {models.map((m) => <option key={m.name}>{m.name}</option>)}
          </select>
        </Field>
        <Field label="Manufacturing year" error={errors.manufacture_year}>
          <select className={cls('manufacture_year')} value={form.manufacture_year} onChange={(e) => set('manufacture_year', e.target.value)}>
            <option value="">Select year</option>
            {years.map((y) => <option key={y}>{y}</option>)}
          </select>
        </Field>
        <Field label="Kilometres driven" error={errors.kms_driven}>
          <input type="number" min="0" inputMode="numeric" placeholder="e.g. 45000" className={cls('kms_driven')}
            value={form.kms_driven} onChange={(e) => set('kms_driven', e.target.value)} />
        </Field>
        <Field label="Fuel type" error={errors.fuel_type}>
          <select className={cls('fuel_type')} value={form.fuel_type} onChange={(e) => set('fuel_type', e.target.value)}>
            <option value="">Select fuel</option>
            {fuels.map((f) => <option key={f}>{f}</option>)}
          </select>
        </Field>
        <Field label="Transmission" error={errors.transmission}>
          <select className={cls('transmission')} value={form.transmission} onChange={(e) => set('transmission', e.target.value)}>
            <option value="">Select transmission</option>
            {trans.map((t) => <option key={t}>{t}</option>)}
          </select>
        </Field>
        <Field label="Ownership" error={errors.ownership}>
          <select className={cls('ownership')} value={form.ownership} onChange={(e) => set('ownership', e.target.value)}>
            <option value="">Select owner count</option>
            {opts.ownership.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
          </select>
        </Field>
        <Field label="Engine capacity (cc)" error={errors.engine_cc}>
          <input type="number" min={opts.engine_range[0]} max={opts.engine_range[1]} placeholder="e.g. 1197"
            className={cls('engine_cc')} value={form.engine_cc} onChange={(e) => set('engine_cc', e.target.value)} />
        </Field>
        <Field label="Seats" error={errors.seats}>
          <select className={cls('seats')} value={form.seats} onChange={(e) => set('seats', e.target.value)}>
            <option value="">Select seats</option>
            {opts.seats.map((s) => <option key={s} value={s}>{s} seats</option>)}
          </select>
        </Field>
        <div className="flex items-end">
          <button type="submit" className="btn-primary w-full" disabled={submitting}>
            {submitting ? <><Loader2 className="h-4 w-4 animate-spin" /> Calculating...</> : <><Sparkles className="h-4 w-4" /> Predict price</>}
          </button>
        </div>
      </form>
    </section>
  )
}
