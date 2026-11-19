import { createContext, useCallback, useContext, useState } from 'react'
import { AlertCircle, CheckCircle2, X } from 'lucide-react'

const ToastContext = createContext(null)
export const useToast = () => useContext(ToastContext)

// Success / error notifications shown top-right; each disappears after 4.5 s.
export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  const dismiss = useCallback((id) => setToasts((t) => t.filter((x) => x.id !== id)), [])
  const push = useCallback((type, message) => {
    const id = crypto.randomUUID()
    setToasts((t) => [...t, { id, type, message }])
    setTimeout(() => dismiss(id), 4500)
  }, [dismiss])

  const api = { success: (m) => push('success', m), error: (m) => push('error', m) }

  return (
    <ToastContext.Provider value={api}>
      {children}
      <div className="fixed right-4 top-4 z-50 flex w-[min(92vw,22rem)] flex-col gap-2" aria-live="polite">
        {toasts.map((t) => (
          <div key={t.id} role="status"
            className={`flex animate-pop items-start gap-3 rounded-xl border bg-white p-3.5 text-sm shadow-lg ${t.type === 'error' ? 'border-signal' : 'border-teal'}`}>
            {t.type === 'error'
              ? <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-signal" />
              : <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-teal" />}
            <p className="flex-1">{t.message}</p>
            <button onClick={() => dismiss(t.id)} aria-label="Dismiss"><X className="h-4 w-4 text-steel" /></button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}
