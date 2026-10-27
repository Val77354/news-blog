import { useState } from 'react'
import { PODCAST_SOURCES } from '../constants'
import { uploadImage } from '../api/uploads'
import ImagePicker from '../components/ImagePicker'
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
  const [coverFile, setCoverFile] = useState(null)
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
      let coverUrl = values.cover_image_url || null
      if (coverFile) {
        coverUrl = (await uploadImage(coverFile)).url
        setValues((v) => ({ ...v, cover_image_url: coverUrl }))
        setCoverFile(null)
      }
      await onSubmit({ ...values, cover_image_url: coverUrl })
    } catch (err) {
      setError(err.message)
      setSubmitting(false)
    }
  }

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
      <ImagePicker
        initialUrl={initialValues.cover_image_url}
        onFileSelected={setCoverFile}
        caption="Cover image (optional)"
      />
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
