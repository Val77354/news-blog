import { useState } from 'react'
import { PODCAST_SOURCES } from '../constants'
import { resolveImageUrl } from '../api/posts'
import './PodcastForm.css'

const EMPTY = {
  title: '',
  host: '',
  description: '',
  cover_image_url: '',
  source: '',
  external_url: '',
}

export default function PodcastForm({ initialValues = EMPTY, onSubmit, submitLabel = 'Add Podcast' }) {
  const [values, setValues] = useState(initialValues)
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
      await onSubmit({ ...values, cover_image_url: values.cover_image_url || null })
    } catch (err) {
      setError(err.message)
      setSubmitting(false)
    }
  }

  const preview = values.cover_image_url && /^https?:\/\/\S+\.\S+/.test(values.cover_image_url)
    ? resolveImageUrl(values.cover_image_url)
    : null

  return (
    <form className="podcast-form" onSubmit={handleSubmit}>
      <label>
        Title
        <input value={values.title} onChange={update('title')} required />
      </label>
      <div className="podcast-form-row">
        <label>
          Host
          <input value={values.host} onChange={update('host')} required />
        </label>
        <label>
          Source
          <select value={values.source} onChange={update('source')} required>
            <option value="" disabled>
              Select a source
            </option>
            {PODCAST_SOURCES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </label>
      </div>
      <label>
        Description
        <textarea value={values.description} onChange={update('description')} required />
      </label>
      <label>
        Cover image URL (optional)
        <input
          type="url"
          value={values.cover_image_url ?? ''}
          onChange={update('cover_image_url')}
          placeholder="https://..."
        />
      </label>
      {preview && <img src={preview} alt="" className="podcast-form-image-preview" />}
      <label>
        External link
        <input type="url" value={values.external_url} onChange={update('external_url')} required />
      </label>
      <div className="podcast-form-actions">
        <button className="btn btn-primary" type="submit" disabled={submitting}>
          {submitting ? 'Saving…' : submitLabel}
        </button>
        {error && <span className="state-message error">{error}</span>}
      </div>
    </form>
  )
}
