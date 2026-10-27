import { API_URL, apiFetch, withQuery } from './client'

export { API_URL }

export function resolveImageUrl(imageUrl) {
  if (!imageUrl) return null
  return imageUrl.startsWith('http') ? imageUrl : `${API_URL}${imageUrl}`
}

export function listPosts({ category, countries, q } = {}) {
  return apiFetch(withQuery('/posts', { category, countries: countries?.join(','), q }))
}

export const getPost = (id) => apiFetch(`/posts/${id}`)
export const createPost = (post) => apiFetch('/posts', { method: 'POST', json: post })
export const updatePost = (id, post) => apiFetch(`/posts/${id}`, { method: 'PUT', json: post })
export const deletePost = (id) => apiFetch(`/posts/${id}`, { method: 'DELETE' })
