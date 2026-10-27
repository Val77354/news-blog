// Form checks that match the backend rules (backend/app/schemas.py), so
// mistakes are shown right away instead of after sending. The backend still
// checks everything again; these only make the forms friendlier.

// Letters in any language, with spaces . ' - between words. No numbers or symbols.
const NAME_RE = /^\p{L}+(?:[ .'’-]+\p{L}+)*\.?$/u
const LETTER_RE = /\p{L}/gu
const CONTROL_RE = /[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/ // eslint-disable-line no-control-regex
const WEB_URL_RE = /^https?:\/\/[^\s/$.?#][^\s<>"']*$/i

const letters = (s) => (s.match(LETTER_RE) || []).length

function length(value, min, max) {
  const n = value.trim().length
  if (n === 0) return 'This field is required.'
  if (n < min) return `Must be at least ${min} characters.`
  if (n > max) return `Must be at most ${max} characters (now ${n}).`
  return null
}

function readable(value, minLetters) {
  if (CONTROL_RE.test(value)) return 'Contains invisible control characters.'
  if (letters(value) < minLetters) return `Must contain at least ${minLetters} letters, not just numbers or symbols.`
  return null
}

export function checkName(value) {
  return length(value, 2, 100) ||
    (NAME_RE.test(value.trim()) ? null : "Use only letters, spaces, and . ' - (no numbers or symbols).")
}

export function checkHeadline(value) {
  if (/[\r\n]/.test(value)) return 'Must be a single line.'
  return length(value, 3, 200) || readable(value, 3)
}

export function checkBody(value, max) {
  return length(value, 10, max) || readable(value, 5)
}

export function checkWebUrl(value) {
  if (!value.trim()) return 'This field is required.'
  return WEB_URL_RE.test(value.trim()) ? null : 'Enter a full link starting with http:// or https://'
}

export function checkChoice(value, options) {
  return options.includes(value) ? null : 'Please choose one.'
}

export function checkPost(v, { categories, countries }) {
  return compact({
    title: checkHeadline(v.title),
    author: checkName(v.author),
    category: checkChoice(v.category, categories),
    country: checkChoice(v.country, countries),
    content: checkBody(v.content, 50000),
  })
}

export function checkPodcast(v, { sources }) {
  return compact({
    title: checkHeadline(v.title),
    host: checkName(v.host),
    source: checkChoice(v.source, sources),
    description: checkBody(v.description, 5000),
    external_url: checkWebUrl(v.external_url),
  })
}

// Keep only the fields that have a problem: {} means everything is fine.
function compact(errors) {
  return Object.fromEntries(Object.entries(errors).filter(([, msg]) => msg))
}
