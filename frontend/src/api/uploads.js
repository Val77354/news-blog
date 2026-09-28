import { API_URL } from './posts'

export async function uploadImage(file) {
  const formData = new FormData()
  formData.append('file', file)

  const res = await fetch(`${API_URL}/uploads/image`, {
    method: 'POST',
    body: formData,
  })

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

  return res.json()
}
