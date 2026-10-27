import { useState } from 'react'
import { CATEGORIES, COUNTRIES, COUNTRY_FLAGS } from '../constants'
import { uploadImage } from '../api/uploads'
import { checkPost } from '../utils/validation'
import FormField from './FormField'
import ImagePicker from './ImagePicker'
import './PostForm.css'

const EMPTY = { title: '', content: '', author: '', category: '', country: '', image_url: null, status: 'published' }

export default function PostForm({ initialValues = EMPTY, onSubmit, submitLabel = 'Publish' }) {
  const [values, setValues] = useState(initialValues)
  const [imageFile, setImageFile] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)
  const [fieldErrors, setFieldErrors] = useState({})
  const [checked, setChecked] = useState(false) // show errors as you type after the first save attempt

  function update(field) {
    return (e) => {
      const next = { ...values, [field]: e.target.value }
      setValues(next)
      if (checked) setFieldErrors(checkPost(next, { categories: CATEGORIES, countries: COUNTRIES }))
    }
  }

  async function handleSubmit(e) {
    e.preventDefault()
    const problems = checkPost(values, { categories: CATEGORIES, countries: COUNTRIES })
    setChecked(true)
    setFieldErrors(problems)
    if (Object.keys(problems).length > 0) {
      setError('Please fix the highlighted fields.')
      return
    }
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
    <form className="post-form" onSubmit={handleSubmit} noValidate>
      <FormField label="Title" error={fieldErrors.title}>
        <input value={values.title} onChange={update('title')} maxLength={200} aria-invalid={!!fieldErrors.title} />
      </FormField>
      <div className="post-form-row">
        <FormField label="Author" error={fieldErrors.author} hint="Letters only, e.g. Anna O'Neil-Smith">
          <input value={values.author} onChange={update('author')} maxLength={100} aria-invalid={!!fieldErrors.author} />
        </FormField>
        <FormField label="Category" error={fieldErrors.category}>
          <select value={values.category} onChange={update('category')} aria-invalid={!!fieldErrors.category}>
            <option value="" disabled>
              Select a category
            </option>
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </FormField>
        <FormField label="Country" error={fieldErrors.country}>
          <select value={values.country} onChange={update('country')} aria-invalid={!!fieldErrors.country}>
            <option value="" disabled>
              Select a country
            </option>
            {COUNTRIES.map((c) => (
              <option key={c} value={c}>
                {COUNTRY_FLAGS[c]} {c}
              </option>
            ))}
          </select>
        </FormField>
      </div>
      <FormField label="Content" error={fieldErrors.content}>
        <textarea value={values.content} onChange={update('content')} maxLength={50000} aria-invalid={!!fieldErrors.content} />
      </FormField>
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
