import { useState } from 'react'
import './PostForm.css'

const EMPTY = { title: '', content: '', author: '', category: '' }

export default function PostForm({ initialValues = EMPTY, onSubmit, submitLabel = 'Publish' }) {
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
      await onSubmit(values)
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
          <input value={values.category} onChange={update('category')} required />
        </label>
      </div>
      <label>
        Content
        <textarea value={values.content} onChange={update('content')} required />
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
