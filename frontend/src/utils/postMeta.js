export function getReadTime(content) {
  const words = content.trim().split(/\s+/).filter(Boolean).length
  const minutes = Math.max(1, Math.round(words / 200))
  return `${minutes} min read`
}

// Real view count from the server, e.g. 1234 -> "1.2K views"
export function formatViews(count = 0) {
  const n = count >= 1000 ? `${(count / 1000).toFixed(1)}K` : `${count}`
  return `${n} ${count === 1 ? 'view' : 'views'}`
}

// Date shown to readers: when it was published (drafts: when it was created)
export function displayDate(post, options) {
  return new Date(post.published_at || post.created_at).toLocaleDateString(undefined, options)
}
