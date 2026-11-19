import { useEffect, useState } from 'react'

// Mechanical-odometer style counter: each digit is a column that rolls to its value.
export default function Odometer({ value, digits = 6, label }) {
  const [shown, setShown] = useState(0)
  useEffect(() => {
    const id = requestAnimationFrame(() => setShown(value ?? 0))
    return () => cancelAnimationFrame(id)
  }, [value])

  const text = String(Math.max(0, Math.round(shown))).padStart(digits, '0').slice(-digits)
  return (
    <div role="img" aria-label={`${label}: ${value ?? 'unavailable'}`}>
      <div className="flex gap-1.5">
        {text.split('').map((d, i) => (
          <div key={i} className="h-16 w-10 overflow-hidden rounded-md border border-white/15 bg-black/40 sm:h-20 sm:w-12">
            <div className="transition-transform duration-[1400ms] ease-out"
              style={{ transform: `translateY(-${Number(d) * 10}%)`, transitionDelay: `${i * 90}ms` }}>
              {Array.from({ length: 10 }, (_, n) => (
                <div key={n} className="grid h-16 place-items-center font-display text-4xl font-extrabold text-white sm:h-20 sm:text-5xl">{n}</div>
              ))}
            </div>
          </div>
        ))}
      </div>
      <p className="mt-3 text-sm text-white/70">{label}</p>
    </div>
  )
}
