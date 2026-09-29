import { Link } from 'react-router-dom'
import { useInView } from '../hooks/useInView'
import { resolveImageUrl } from '../api/posts'
import { COUNTRY_FLAGS } from '../constants'
import { getTags, getReadTime, getStats } from '../utils/postMeta'
import './PostCard.css'

function excerpt(content, length = 140) {
  const flat = content.replace(/\s+/g, ' ').trim()
  return flat.length > length ? `${flat.slice(0, length)}…` : flat
}

export default function PostCard({ post, index = 0 }) {
  const [ref, inView] = useInView()
  const date = new Date(post.created_at).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
  const stats = getStats(post)

  function handleMouseMove(e) {
    const rect = e.currentTarget.getBoundingClientRect()
    e.currentTarget.style.setProperty('--mouse-x', `${e.clientX - rect.left}px`)
    e.currentTarget.style.setProperty('--mouse-y', `${e.clientY - rect.top}px`)
  }

  return (
    <Link
      to={`/posts/${post.id}`}
      className={`post-card${inView ? ' fade-up-item' : ''}`}
      style={inView ? { animationDelay: `${Math.min(index, 8) * 60}ms` } : { opacity: 0 }}
      ref={ref}
      onMouseMove={handleMouseMove}
    >
      {post.image_url && (
        <img
          src={resolveImageUrl(post.image_url)}
          alt=""
          className="post-card-image"
          onError={(e) => {
            e.currentTarget.style.display = 'none'
          }}
        />
      )}
      <div className="badge-row">
        <span className="category-pill">{post.category}</span>
        <span className="country-badge">
          {COUNTRY_FLAGS[post.country]} {post.country}
        </span>
      </div>
      <h2>{post.title}</h2>
      <p className="post-card-excerpt">{excerpt(post.content)}</p>
      <div className="post-card-meta">
        {post.author} · {date}
      </div>
      <div className="post-card-tags">
        {getTags(post).map((tag) => (
          <span key={tag} className="tag-chip">
            {tag}
          </span>
        ))}
      </div>
      <div className="post-card-stats">
        <span>{getReadTime(post.content)}</span>
        <span>{stats.views} views</span>
        <span>{stats.comments} comments</span>
      </div>
    </Link>
  )
}
