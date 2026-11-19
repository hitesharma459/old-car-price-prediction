import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import Spinner from '../components/Spinner.jsx'
import ErrorState from '../components/ErrorState.jsx'
import useFetch from '../hooks/useFetch.js'
import { api } from '../services/api.js'
import { formatINR, formatNumber } from '../utils/format.js'

const stack = [
  ['Frontend', 'React, Vite, Tailwind CSS, Recharts, Lucide icons'],
  ['Backend', 'Python, FastAPI, Pydantic, Uvicorn'],
  ['Machine learning', 'Pandas, NumPy, scikit-learn, Matplotlib, Seaborn, Joblib'],
  ['Database', 'SQLite with SQLAlchemy (PostgreSQL supported for deployment)'],
]
const workflow = ['Parse text fields (prices in lakh/crore, "86,226 kms", "1956 cc") into numbers',
  'Remove duplicates and invalid rows; analyse outliers',
  'Derive brand and model from the car name; engineer age, log-kilometres and km per year',
  'Encode categories and scale numbers inside one pipeline (fitted on training data only)',
  'Tune and cross-validate five regression algorithms',
  'Select the best model on cross-validation, report on a held-out test set, serialize with Joblib']

export default function About() {
  const { data, error, loading, reload } = useFetch(() => api.modelInfo())
  if (loading) return <Spinner label="Loading model details..." />
  if (error) return <div className="px-4 py-16"><ErrorState error={error} onRetry={reload} /></div>

  const t = data.test_metrics
  const chart = data.model_comparison.map((m) => ({ name: m.model, 'Test MAE': Math.round(m.test.mae) }))

  return (
    <section className="mx-auto max-w-5xl px-4 py-12">
      <h1 className="text-3xl font-bold sm:text-4xl">About the project</h1>
      <p className="mt-3 max-w-2xl text-steel">
        CarWorth estimates the resale price of an old car with a regression model trained on a dataset of
        {' '}{formatNumber(data.cleaning.clean_rows)} used-car listings. Results are indicative, not guaranteed prices.
      </p>

      <h2 className="mt-10 text-2xl font-bold">Best model: {data.best_model}</h2>
      <div className="mt-4 grid grid-cols-2 gap-4 md:grid-cols-5">
        {[['R²', t.r2.toFixed(3)], ['MAE', formatINR(t.mae)], ['RMSE', formatINR(t.rmse)],
          ['MSE', t.mse.toExponential(2)], ['MAPE', `${t.mape_pct.toFixed(1)}%`]].map(([k, v]) => (
          <div key={k} className="card !p-4"><p className="text-xs text-steel">{k} (test set)</p><p className="mt-1 font-display text-xl font-bold">{v}</p></div>
        ))}
      </div>
      <p className="mt-2 text-xs text-steel">Selection metric: {data.selection_metric}. Test set: {formatNumber(data.split.test_rows)} unseen cars.</p>

      <div className="card mt-6">
        <h3 className="font-bold">Model comparison - mean absolute error on the test set</h3>
        <div className="mt-4 h-64">
          <ResponsiveContainer>
            <BarChart data={chart}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} /><XAxis dataKey="name" tick={{ fontSize: 12 }} />
              <YAxis tickFormatter={(v) => `${Math.round(v / 1000)}k`} width={50} />
              <Tooltip formatter={(v) => formatINR(v)} /><Bar dataKey="Test MAE" fill="#D8312B" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="mt-4 overflow-x-auto">
          <table className="w-full min-w-[560px] text-left text-sm">
            <thead className="text-steel"><tr>
              {['Algorithm', 'CV R² (log)', 'Test R²', 'Test MAE', 'Test RMSE'].map((h) => <th key={h} className="pb-2 font-medium">{h}</th>)}
            </tr></thead>
            <tbody>
              {data.model_comparison.map((m) => (
                <tr key={m.model} className={`border-t border-line ${m.model === data.best_model ? 'bg-teal/10 font-medium' : ''}`}>
                  <td className="py-2">{m.model}</td><td>{m.cv_r2_log.toFixed(3)}</td><td>{m.test.r2.toFixed(3)}</td>
                  <td>{formatINR(m.test.mae)}</td><td>{formatINR(m.test.rmse)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="mt-6 grid gap-5 md:grid-cols-2">
        <div className="card">
          <h3 className="font-bold">Technology stack</h3>
          <dl className="mt-3 space-y-3 text-sm">{stack.map(([k, v]) => <div key={k}><dt className="font-medium">{k}</dt><dd className="text-steel">{v}</dd></div>)}</dl>
        </div>
        <div className="card">
          <h3 className="font-bold">Project workflow</h3>
          <ol className="mt-3 list-decimal space-y-2 pl-5 text-sm text-steel">{workflow.map((w) => <li key={w}>{w}</li>)}</ol>
        </div>
      </div>

      {data.notes?.length > 0 && (
        <ul className="mt-6 list-disc space-y-1 pl-5 text-sm text-steel">{data.notes.map((n) => <li key={n}>{n}</li>)}</ul>
      )}
    </section>
  )
}
