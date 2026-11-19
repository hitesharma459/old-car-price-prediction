// Thin wrapper around fetch for the FastAPI backend.
const BASE = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '')

export class ApiError extends Error {
  constructor(message, status) {
    super(message)
    this.status = status
  }
}

// FastAPI returns {detail: "text"} or {detail: [{loc, msg}, ...]} for validation errors.
function readDetail(detail) {
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail.map((d) => `${(d.loc || []).slice(1).join('.')}: ${d.msg}`).join('; ')
  }
  return 'Something went wrong'
}

async function request(path, options = {}) {
  let res
  try {
    res = await fetch(`${BASE}${path}`, {
      headers: { 'Content-Type': 'application/json' },
      ...options,
    })
  } catch {
    throw new ApiError('Cannot reach the server. Is the backend running?', 0)
  }
  const body = await res.json().catch(() => ({}))
  if (!res.ok) throw new ApiError(readDetail(body.detail), res.status)
  return body
}

export const api = {
  health: () => request('/health'),
  options: () => request('/options'),
  modelInfo: () => request('/model-info'),
  predict: (payload) => request('/predict', { method: 'POST', body: JSON.stringify(payload) }),
  history: (limit = 50, offset = 0) => request(`/history?limit=${limit}&offset=${offset}`),
  prediction: (id) => request(`/history/${id}`),
  deletePrediction: (id) => request(`/history/${id}`, { method: 'DELETE' }),
  stats: () => request('/stats'),
}
