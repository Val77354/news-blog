import { Link } from 'react-router-dom'
import { useInView } from '../hooks/useInView'
import { API_URL } from '../api/posts'
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
        <img src={`${API_URL}${post.image_url}`} alt="" className="post-card-image" />
      )}
      <div className="badge-row">
        <span className="category-pill">{post.category}</span>
        <span className="country-badge">{post.country}</span>
      </div>
      <h2>{post.title}</h2>
      <p className="post-card-excerpt">{excerpt(post.content)}</p>
      <div className="post-card-meta">
        {post.author} · {date}
      </div>
    </Link>
  )
}
