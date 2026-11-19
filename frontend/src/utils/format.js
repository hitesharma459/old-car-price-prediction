// Indian-rupee helpers. Lakh = 1e5, Crore = 1e7.
const inr = new Intl.NumberFormat('en-IN', { maximumFractionDigits: 0 })

export const formatINR = (n) => `₹${inr.format(Math.round(n))}`

export function formatShort(n) {
  if (n >= 1e7) return `₹${(n / 1e7).toFixed(2)} Cr`
  if (n >= 1e5) return `₹${(n / 1e5).toFixed(2)} L`
  return formatINR(n)
}

export const formatNumber = (n) => inr.format(n)

export const formatDate = (iso) =>
  new Date(iso).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' })
