export default function Footer() {
  return (
    <footer className="border-t border-line bg-white">
      <div className="mx-auto max-w-6xl px-4 py-8 text-sm text-steel">
        <p className="font-medium text-ink">CarWorth - Old Car Price Prediction</p>
        <p className="mt-1 max-w-2xl">
          Estimates come from a machine-learning model trained on a historical dataset of used-car
          listings. They are indicative only and not a guaranteed market price.
        </p>
      </div>
    </footer>
  )
}
