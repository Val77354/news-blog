import { useState } from 'react'
import { PODCAST_SOURCES } from '../constants'
import { uploadImage } from '../api/uploads'
import { checkPodcast } from '../utils/validation'
import FormField from '../components/FormField'
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
  const [fieldErrors, setFieldErrors] = useState({})
  const [checked, setChecked] = useState(false)

  function update(field) {
    return (e) => {
      const next = { ...values, [field]: e.target.value }
      setValues(next)
      if (checked) setFieldErrors(checkPodcast(next, { sources: PODCAST_SOURCES }))
    }
  }

  async function handleSubmit(e) {
    e.preventDefault()
    const problems = checkPodcast(values, { sources: PODCAST_SOURCES })
    setChecked(true)
    setFieldErrors(problems)
    if (Object.keys(problems).length > 0) {
      setError('Please fix the highlighted fields.')
      return
    }
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
    <form className="podcast-form" onSubmit={handleSubmit} noValidate>
      <FormField label="Title" error={fieldErrors.title}>
        <input value={values.title} onChange={update('title')} maxLength={200} aria-invalid={!!fieldErrors.title} />
      </FormField>
      <div className="podcast-form-row">
        <FormField label="Host" error={fieldErrors.host} hint="Letters only">
          <input value={values.host} onChange={update('host')} maxLength={100} aria-invalid={!!fieldErrors.host} />
        </FormField>
        <FormField label="Source" error={fieldErrors.source}>
          <select value={values.source} onChange={update('source')} aria-invalid={!!fieldErrors.source}>
            <option value="" disabled>
              Select a source
            </option>
            {PODCAST_SOURCES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </FormField>
      </div>
      <FormField label="Description" error={fieldErrors.description}>
        <textarea value={values.description} onChange={update('description')} maxLength={5000} aria-invalid={!!fieldErrors.description} />
      </FormField>
      <ImagePicker
        initialUrl={initialValues.cover_image_url}
        onFileSelected={setCoverFile}
        caption="Cover image (optional)"
      />
      <FormField label="External link" error={fieldErrors.external_url} hint="e.g. https://open.spotify.com/show/...">
        <input type="url" value={values.external_url} onChange={update('external_url')} maxLength={500} aria-invalid={!!fieldErrors.external_url} />
      </FormField>
      <div className="podcast-form-actions">
        <button className="btn btn-primary" type="submit" disabled={submitting}>
          {submitting ? 'Saving…' : submitLabel}
        </button>
        {error && <span className="state-message error">{error}</span>}
      </div>
    </form>
  )
}
