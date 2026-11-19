export default function Spinner({ label = 'Loading...' }) {
  return (
    <div className="flex items-center justify-center gap-3 py-16 text-steel" role="status">
      <span className="h-5 w-5 animate-spin rounded-full border-2 border-line border-t-signal" />
      <span className="text-sm">{label}</span>
    </div>
  )
}
