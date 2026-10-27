// One place for talking to the backend.
//
// Normally the backend serves this website itself, so the API is simply /api
// on the same address. VITE_API_URL is only needed if the API lives somewhere
// else, e.g. VITE_API_URL=https://api.example.com
export const API_ORIGIN = import.meta.env.VITE_API_URL || ''
export const API_URL = `${API_ORIGIN}/api`

const FIELD_LABELS = { external_url: 'link', image_url: 'image', cover_image_url: 'cover image', feed_url: 'feed address' }

// Turn the backend's validation list into one readable sentence:
// "author: can only contain letters, spaces, and . ' - (no numbers or symbols)"
function describeValidationErrors(list) {
  return list
    .map((e) => {
      const field = e.loc?.[e.loc.length - 1]
      const msg = String(e.msg || '').replace(/^Value error, /, '')
      return typeof field === 'string' && field !== 'body' ? `${FIELD_LABELS[field] || field}: ${msg}` : msg
    })
    .join('; ')
}

export class ApiError extends Error {
  constructor(message, status) {
    super(message)
    this.status = status
  }
}

async function handleResponse(res) {
  if (!res.ok) {
    let detail = res.statusText || `Request failed (${res.status})`
    try {
      const data = await res.json()
      detail = Array.isArray(data.detail) ? describeValidationErrors(data.detail) : data.detail || detail
    } catch (err) {
      console.warn('Error response had no JSON body', err)
    }
    if (res.status === 401) detail = 'Your login has expired. Please log in again.'
    throw new ApiError(detail, res.status)
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
export async function apiFetch(path, { method = 'GET', json, body } = {}) {
  // Only writes need the header; leaving it off GETs keeps reads fast (no CORS preflight).
  const headers = method === 'GET' ? {} : { 'X-Requested-With': 'XMLHttpRequest' }
  if (json !== undefined) {
    headers['Content-Type'] = 'application/json'
    body = JSON.stringify(json)
  }
  let res
  try {
    res = await fetch(`${API_URL}${path}`, { method, headers, body, credentials: 'include' })
  } catch (err) {
    console.error('Network error', method, path, err)
    throw new ApiError("Can't reach the server. Check your connection and try again.", 0)
  }
  return handleResponse(res)
}

export function withQuery(path, params) {
  const qs = new URLSearchParams(Object.entries(params).filter(([, v]) => v)).toString()
  return qs ? `${path}?${qs}` : path
}
