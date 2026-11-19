import { useState } from 'react'
import { Link, NavLink } from 'react-router-dom'
import { Car, Menu, X } from 'lucide-react'

const links = [
  { to: '/', label: 'Home', end: true },
  { to: '/predict', label: 'Predict' },
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/about', label: 'About' },
]

export default function Navbar() {
  const [open, setOpen] = useState(false)
  const cls = ({ isActive }) =>
    `rounded-lg px-3 py-2 text-sm font-medium transition ${isActive ? 'bg-ink text-white' : 'text-ink hover:bg-white'}`

  return (
    <header className="sticky top-0 z-40 border-b border-line bg-paper/90 backdrop-blur">
      <nav className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <Link to="/" className="flex items-center gap-2 font-display text-lg font-extrabold">
          <span className="grid h-8 w-8 place-items-center rounded-lg bg-ink text-white"><Car className="h-4 w-4" /></span>
          CarWorth
        </Link>
        <div className="hidden items-center gap-1 md:flex">
          {links.map((l) => <NavLink key={l.to} {...l} className={cls}>{l.label}</NavLink>)}
          <Link to="/predict" className="btn-primary ml-2 !py-2">Get estimate</Link>
        </div>
        <button className="md:hidden" onClick={() => setOpen(!open)} aria-label="Toggle menu" aria-expanded={open}>
          {open ? <X /> : <Menu />}
        </button>
      </nav>
      {open && (
        <div className="space-y-1 border-t border-line px-4 pb-4 pt-2 md:hidden">
          {links.map((l) => (
            <NavLink key={l.to} {...l} className={cls} onClick={() => setOpen(false)}>
              <span className="block">{l.label}</span>
            </NavLink>
          ))}
        </div>
      )}
    </header>
  )
}
