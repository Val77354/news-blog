import { API_URL } from './posts'

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

export function listPodcasts() {
  return fetch(`${API_URL}/podcasts`).then(handleResponse)
}

export function getPodcast(id) {
  return fetch(`${API_URL}/podcasts/${id}`).then(handleResponse)
}

export function createPodcast(podcast) {
  return fetch(`${API_URL}/podcasts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(podcast),
  }).then(handleResponse)
}

export function updatePodcast(id, podcast) {
  return fetch(`${API_URL}/podcasts/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(podcast),
  }).then(handleResponse)
}

export function deletePodcast(id) {
  return fetch(`${API_URL}/podcasts/${id}`, { method: 'DELETE' }).then(handleResponse)
}
