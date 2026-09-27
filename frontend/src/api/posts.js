const API_URL = 'http://localhost:8000'

async function handleResponse(res) {
  if (!res.ok) {
    let detail = res.statusText
    try {
      const data = await res.json()
      detail = data.detail || detail
    } catch {
      // response had no JSON body
    }
    throw new Error(detail)
  }
  if (res.status === 204) return null
  return res.json()
}

export function listPosts() {
  return fetch(`${API_URL}/posts`).then(handleResponse)
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
