// One place for talking to the backend.
// Set VITE_API_URL in frontend/.env for production, e.g. https://api.example.com
export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function handleResponse(res) {
  if (!res.ok) {
    let detail = res.statusText
    try {
      const data = await res.json()
      const d = data.detail
      detail = Array.isArray(d) ? d.map((e) => e.msg).join(', ') : d || detail
    } catch {
      // response had no JSON body
    }
    throw new Error(detail)
  }
  if (res.status === 204) return null
  return res.json()
}

/**
 * apiFetch('/posts')                              -> GET
 * apiFetch('/posts', { method: 'POST', json })    -> JSON body
 * apiFetch('/uploads/image', { method: 'POST', body: formData })
 *
 * Always sends the admin login cookie. Writes also carry the X-Requested-With
 * header the backend requires (CSRF protection).
 */
export function apiFetch(path, { method = 'GET', json, body } = {}) {
  // Only writes need the header; leaving it off GETs keeps reads fast (no CORS preflight).
  const headers = method === 'GET' ? {} : { 'X-Requested-With': 'XMLHttpRequest' }
  if (json !== undefined) {
    headers['Content-Type'] = 'application/json'
    body = JSON.stringify(json)
  }
  return fetch(`${API_URL}${path}`, { method, headers, body, credentials: 'include' }).then(handleResponse)
}

export function withQuery(path, params) {
  const qs = new URLSearchParams(Object.entries(params).filter(([, v]) => v)).toString()
  return qs ? `${path}?${qs}` : path
}
