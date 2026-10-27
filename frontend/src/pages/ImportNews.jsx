import { useState } from 'react'
import { Link } from 'react-router-dom'
import { importNews } from '../api/importer'
import { CATEGORIES, COUNTRIES, COUNTRY_FLAGS } from '../constants'
import { checkChoice, checkWebUrl } from '../utils/validation'
import FormField from '../components/FormField'
import '../components/PostForm.css'

// Well-known public news feeds to start from. Any RSS or Atom feed works.
const SUGGESTED_FEEDS = [
  { label: 'BBC News — Europe', url: 'https://feeds.bbci.co.uk/news/world/europe/rss.xml', category: 'World', country: 'United Kingdom' },
  { label: 'BBC News — Technology', url: 'https://feeds.bbci.co.uk/news/technology/rss.xml', category: 'Technology', country: 'United Kingdom' },
  { label: 'BBC News — Business', url: 'https://feeds.bbci.co.uk/news/business/rss.xml', category: 'Business', country: 'United Kingdom' },
  { label: 'The Guardian — Science', url: 'https://www.theguardian.com/science/rss', category: 'Science', country: 'United Kingdom' },
  { label: 'France 24 — Europe', url: 'https://www.france24.com/en/europe/rss', category: 'World', country: 'France' },
  { label: 'DW — Germany', url: 'https://rss.dw.com/rdf/rss-en-ger', category: 'World', country: 'Germany' },
]

export default function ImportNews() {
  const [form, setForm] = useState({ feed_url: '', category: '', country: '', limit: 10 })
  const [fieldErrors, setFieldErrors] = useState({})
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  function set(field) {
    return (e) => setForm((f) => ({ ...f, [field]: e.target.value }))
  }

  function applySuggestion(e) {
    const feed = SUGGESTED_FEEDS.find((f) => f.url === e.target.value)
    if (feed) setForm((f) => ({ ...f, feed_url: feed.url, category: feed.category, country: feed.country }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    const problems = Object.fromEntries(
      Object.entries({
        feed_url: checkWebUrl(form.feed_url),
        category: checkChoice(form.category, CATEGORIES),
        country: checkChoice(form.country, COUNTRIES),
      }).filter(([, msg]) => msg),
    )
    setFieldErrors(problems)
    if (Object.keys(problems).length > 0) return

    setBusy(true)
    setError(null)
    setResult(null)
    try {
      setResult(await importNews({ ...form, feed_url: form.feed_url.trim(), limit: Number(form.limit) }))
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="page container">
      <h1>Import news</h1>
      <p className="state-message">
        Bring in the latest headlines from a news site's RSS feed. Each story is saved as a <strong>draft</strong> with
        a short summary and a link to the original, so nothing is public until you review and publish it.
      </p>

      <form className="post-form" onSubmit={handleSubmit} noValidate>
        <label>
          Suggested feeds
          <select value="" onChange={applySuggestion}>
            <option value="">Pick one to fill in the form…</option>
            {SUGGESTED_FEEDS.map((f) => (
              <option key={f.url} value={f.url}>
                {f.label}
              </option>
            ))}
          </select>
        </label>
        <FormField label="Feed address" error={fieldErrors.feed_url} hint="An RSS or Atom link, usually ending in rss or .xml">
          <input type="url" value={form.feed_url} onChange={set('feed_url')} placeholder="https://…/rss.xml" maxLength={500} />
        </FormField>
        <div className="post-form-row">
          <FormField label="Category" error={fieldErrors.category}>
            <select value={form.category} onChange={set('category')}>
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
            <select value={form.country} onChange={set('country')}>
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
          <label>
            How many
            <select value={form.limit} onChange={set('limit')}>
              {[5, 10, 20].map((n) => (
                <option key={n} value={n}>
                  Up to {n} stories
                </option>
              ))}
            </select>
          </label>
        </div>
        <div className="post-form-actions">
          <button className="btn btn-primary" type="submit" disabled={busy}>
            {busy ? 'Importing…' : 'Import as drafts'}
          </button>
          {error && <span className="state-message error">{error}</span>}
        </div>
      </form>

      {result && (
        <div className="import-result">
          <h2>{result.feed_title}</h2>
          <p className="state-message">
            {result.created.length} new draft{result.created.length === 1 ? '' : 's'}
            {result.already_imported > 0 && ` · ${result.already_imported} already imported before`}
            {result.skipped.length > 0 && ` · ${result.skipped.length} skipped (no proper headline)`}
          </p>
          <ul>
            {result.created.map((post) => (
              <li key={post.id}>
                <Link to={`/posts/${post.slug}`}>{post.title}</Link> ·{' '}
                <Link to={`/posts/${post.id}/edit`}>edit &amp; publish</Link>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
