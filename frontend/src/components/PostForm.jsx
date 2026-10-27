import { useState } from 'react'
import { CATEGORIES, COUNTRIES, COUNTRY_FLAGS } from '../constants'
import { uploadImage } from '../api/uploads'
import ImagePicker from './ImagePicker'
import './PostForm.css'

const EMPTY = { title: '', content: '', author: '', category: '', country: '', image_url: null, status: 'published' }

export default function PostForm({ initialValues = EMPTY, onSubmit, submitLabel = 'Publish' }) {
  const [values, setValues] = useState(initialValues)
  const [imageFile, setImageFile] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)

  function update(field) {
    return (e) => setValues((v) => ({ ...v, [field]: e.target.value }))
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
        setValues((v) => ({ ...v, image_url: imageUrl }))
        setImageFile(null)
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
                {COUNTRY_FLAGS[c]} {c}
              </option>
            ))}
          </select>
        </label>
      </div>
      <label>
        Content
        <textarea value={values.content} onChange={update('content')} required />
      </label>
      <ImagePicker initialUrl={initialValues.image_url} onFileSelected={setImageFile} />
      <label>
        Visibility
        <select value={values.status} onChange={update('status')}>
          <option value="published">Published — everyone can read it</option>
          <option value="draft">Draft — only you can see it</option>
        </select>
      </label>
      <div className="post-form-actions">
        <button className="btn btn-primary" type="submit" disabled={submitting}>
          {submitting ? 'Saving…' : submitLabel}
        </button>
        {error && <span className="state-message error">{error}</span>}
      </div>
    </form>
  )
}
