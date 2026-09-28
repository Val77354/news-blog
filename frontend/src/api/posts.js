export const API_URL = 'http://localhost:8000'

export function resolveImageUrl(imageUrl) {
  if (!imageUrl) return null
  return imageUrl.startsWith('http') ? imageUrl : `${API_URL}${imageUrl}`
}

async function handleResponse(res) {
  if (!res.ok) {
    let detail = res.statusText
    try {
      const data = await res.json()
      const d = data.detail
      detail = Array.isArray(d) ? d.map((e) => e.msg).join(', ') : (d || detail)
    } catch {
      // response had no JSON body
    }
    throw new Error(detail)
  }
  if (res.status === 204) return null
  return res.json()
}

export function listPosts({ category, countries } = {}) {
  const params = new URLSearchParams()
  if (category) params.set('category', category)
  if (countries && countries.length > 0) params.set('countries', countries.join(','))
  const qs = params.toString()
  return fetch(`${API_URL}/posts${qs ? `?${qs}` : ''}`).then(handleResponse)
}

export function getPost(id) {
  return fetch(`${API_URL}/posts/${id}`).then(handleResponse)
}

export function createPost(post) {
  return fetch(`${API_URL}/posts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(post),
  }).then(handleResponse)
}

export function updatePost(id, post) {
  return fetch(`${API_URL}/posts/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(post),
  }).then(handleResponse)
}

export function deletePost(id) {
  return fetch(`${API_URL}/posts/${id}`, { method: 'DELETE' }).then(handleResponse)
}
