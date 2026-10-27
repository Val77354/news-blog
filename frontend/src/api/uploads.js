import { apiFetch } from './client'

export function uploadImage(file) {
  const formData = new FormData()
  formData.append('file', file)
  return apiFetch('/uploads/image', { method: 'POST', body: formData })
}
