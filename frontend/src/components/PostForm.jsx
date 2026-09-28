import { useEffect, useState } from 'react'
import { CATEGORIES, COUNTRIES } from '../constants'
import { API_URL } from '../api/posts'
import { uploadImage } from '../api/uploads'
import './PostForm.css'

const EMPTY = { title: '', content: '', author: '', category: '', country: '', image_url: null }

export default function PostForm({ initialValues = EMPTY, onSubmit, submitLabel = 'Publish' }) {
  const [values, setValues] = useState(initialValues)
  const [imageFile, setImageFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(
    initialValues.image_url ? `${API_URL}${initialValues.image_url}` : null,
  )
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    return () => {
      if (previewUrl && previewUrl.startsWith('blob:')) URL.revokeObjectURL(previewUrl)
    }
  }, [previewUrl])

  function update(field) {
    return (e) => setValues((v) => ({ ...v, [field]: e.target.value }))
  }

  function handleFileChange(e) {
    const file = e.target.files[0]
    if (!file) return
    setImageFile(file)
    setPreviewUrl(URL.createObjectURL(file))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      let imageUrl = values.image_url ?? null
      if (imageFile) {
        const result = await uploadImage(imageFile)
        imageUrl = result.url
      }
      await onSubmit({ ...values, image_url: imageUrl })
    } catch (err) {
      setError(err.message)
      setSubmitting(false)
    }
  }

  return (
    <form className="post-form" onSubmit={handleSubmit}>
      <label>
        Title
        <input value={values.title} onChange={update('title')} required />
      </label>
      <div className="post-form-row">
        <label>
          Author
          <input value={values.author} onChange={update('author')} required />
        </label>
        <label>
          Category
          <select value={values.category} onChange={update('category')} required>
            <option value="" disabled>
              Select a category
            </option>
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </label>
        <label>
          Country
          <select value={values.country} onChange={update('country')} required>
            <option value="" disabled>
              Select a country
            </option>
            {COUNTRIES.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </label>
      </div>
      <label>
        Content
        <textarea value={values.content} onChange={update('content')} required />
      </label>
      <div className="post-form-image-field">
        <span className="post-form-image-caption">Image (optional)</span>
        <div className="post-form-image-picker">
          {previewUrl && <img src={previewUrl} alt="" className="post-form-image-preview" />}
          <label className="post-form-file-button">
            {previewUrl ? 'Change image' : 'Choose image'}
            <input
              type="file"
              accept="image/jpeg,image/png,image/webp,image/gif"
              className="post-form-file-input"
              onChange={handleFileChange}
            />
          </label>
        </div>
      </div>
      <div className="post-form-actions">
        <button className="btn btn-primary" type="submit" disabled={submitting}>
          {submitting ? 'Saving…' : submitLabel}
        </button>
        {error && <span className="state-message error">{error}</span>}
      </div>
    </form>
  )
}
