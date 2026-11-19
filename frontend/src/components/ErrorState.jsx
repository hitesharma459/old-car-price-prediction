import { AlertCircle } from 'lucide-react'

export default function ErrorState({ error, onRetry }) {
  return (
    <div className="card mx-auto max-w-lg text-center">
      <AlertCircle className="mx-auto h-8 w-8 text-signal" />
      <p className="mt-3 font-display text-lg font-bold">Something went wrong</p>
      <p className="mt-1 text-sm text-steel">{error?.message || 'Unexpected error'}</p>
      {onRetry && <button onClick={onRetry} className="btn-dark mt-4">Try again</button>}
    </div>
  )
}
