const DESCRIPTORS = ['Analysis', 'Report', 'Feature', 'Briefing', 'Opinion']

export function getTags(post) {
  const descriptor = DESCRIPTORS[post.id % DESCRIPTORS.length]
  return [post.category, post.country, descriptor]
}

export function getReadTime(content) {
  const words = content.trim().split(/\s+/).filter(Boolean).length
  const minutes = Math.max(1, Math.round(words / 200))
  return `${minutes} min read`
}

function seededNumber(seed, min, max) {
  const x = Math.sin(seed * 9973) * 10000
  const frac = x - Math.floor(x)
  return Math.floor(frac * (max - min)) + min
}

export function getStats(post) {
  const views = seededNumber(post.id * 7 + 1, 800, 48000)
  const comments = seededNumber(post.id * 13 + 3, 4, 260)
  return {
    views: views >= 1000 ? `${(views / 1000).toFixed(1)}K` : `${views}`,
    comments,
  }
}
