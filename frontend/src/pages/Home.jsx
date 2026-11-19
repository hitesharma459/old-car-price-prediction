import { Link } from 'react-router-dom'
import { ArrowRight, BarChart3, Database, SlidersHorizontal, Gauge, History, ShieldCheck } from 'lucide-react'
import Odometer from '../components/Odometer.jsx'
import useFetch from '../hooks/useFetch.js'
import { api } from '../services/api.js'
import { formatNumber } from '../utils/format.js'

const features = [
  { icon: Database, title: 'Trained on real listings', text: 'The model learns from the used-car dataset supplied with this project, not generated data.' },
  { icon: SlidersHorizontal, title: 'Simple car details', text: 'Brand, model, year, kilometres, fuel, transmission, owners, engine size and seats.' },
  { icon: Gauge, title: 'Price with a range', text: 'You get a point estimate plus the typical error band measured on held-out cars.' },
  { icon: History, title: 'History you can review', text: 'Every estimate is stored so you can revisit or delete it later.' },
  { icon: BarChart3, title: 'Dashboard', text: 'Charts of your prediction history: brands, price categories and trend.' },
  { icon: ShieldCheck, title: 'Honest about limits', text: 'Estimates are indicative. Condition, location and negotiation still move real prices.' },
]

const steps = [
  { title: 'Describe the car', text: 'Pick the brand and model; engine size and seats are suggested from the data.' },
  { title: 'Model estimates', text: 'Your inputs go through the same preprocessing pipeline used in training.' },
  { title: 'Review the result', text: 'See the estimate, its likely range and a price category.' },
]

export default function Home() {
  const { data: info } = useFetch(() => api.modelInfo())
  const rows = info?.cleaning?.clean_rows

  return (
    <>
      <section className="bg-ink text-white">
        <div className="mx-auto grid max-w-6xl items-center gap-10 px-4 py-16 md:grid-cols-2 md:py-24">
          <div>
            <h1 className="text-4xl font-extrabold leading-[1.05] sm:text-5xl lg:text-6xl">
              What is your used car worth right now?
            </h1>
            <p className="mt-5 max-w-md text-lg text-white/75">
              Enter a few details and get an AI-generated resale estimate in rupees, with a realistic price range.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link to="/predict" className="btn-primary">Predict price <ArrowRight className="h-4 w-4" /></Link>
              <Link to="/about" className="btn border border-white/25 text-white hover:bg-white/10">How it works</Link>
            </div>
          </div>
          <div className="rounded-3xl border border-white/10 bg-ink-soft p-6 sm:p-8">
            <Odometer value={rows} digits={5} label={rows ? 'cars in the cleaned training dataset' : 'training dataset size (connect the backend to load)'} />
            <div className="relative mt-8 h-3 overflow-hidden rounded bg-black/40">
              <div className="road absolute left-0 top-1/2 h-0.5 w-[200%] -translate-y-1/2 animate-road opacity-70" />
            </div>
            <p className="mt-4 text-sm text-white/60">
              {rows ? `${formatNumber(rows)} listings after removing duplicates and invalid rows.` : 'Start the API to see live dataset figures.'}
            </p>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 py-16">
        <h2 className="text-3xl font-bold">Built around the data</h2>
        <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {features.map(({ icon: Icon, title, text }) => (
            <div key={title} className="card">
              <Icon className="h-5 w-5 text-signal" />
              <h3 className="mt-3 text-lg font-bold">{title}</h3>
              <p className="mt-1 text-sm text-steel">{text}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="border-y border-line bg-white">
        <div className="mx-auto max-w-6xl px-4 py-16">
          <h2 className="text-3xl font-bold">How it works</h2>
          <ol className="mt-8 grid gap-6 md:grid-cols-3">
            {steps.map((s, i) => (
              <li key={s.title} className="flex gap-4">
                <span className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-ink font-display font-bold text-white">{i + 1}</span>
                <div><h3 className="font-bold">{s.title}</h3><p className="mt-1 text-sm text-steel">{s.text}</p></div>
              </li>
            ))}
          </ol>
          <Link to="/predict" className="btn-primary mt-10">Try it now</Link>
        </div>
      </section>
    </>
  )
}
