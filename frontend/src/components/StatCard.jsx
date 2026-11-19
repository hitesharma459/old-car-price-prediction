export default function StatCard({ icon: Icon, label, value, hint }) {
  return (
    <div className="card">
      <div className="flex items-center gap-2 text-sm text-steel">
        {Icon && <Icon className="h-4 w-4" />} {label}
      </div>
      <p className="mt-2 font-display text-3xl font-extrabold">{value}</p>
      {hint && <p className="mt-1 text-xs text-steel">{hint}</p>}
    </div>
  )
}
