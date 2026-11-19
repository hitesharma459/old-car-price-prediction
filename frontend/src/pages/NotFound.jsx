import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <section className="mx-auto max-w-xl px-4 py-24 text-center">
      <p className="font-display text-7xl font-extrabold text-signal">404</p>
      <h1 className="mt-2 text-2xl font-bold">This road doesn't lead anywhere</h1>
      <Link to="/" className="btn-dark mt-6">Back to home</Link>
    </section>
  )
}
