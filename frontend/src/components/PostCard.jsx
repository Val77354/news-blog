import { Link } from 'react-router-dom'
import './PostCard.css'

function excerpt(content, length = 140) {
  const flat = content.replace(/\s+/g, ' ').trim()
  return flat.length > length ? `${flat.slice(0, length)}…` : flat
}

export default function PostCard({ post }) {
  const date = new Date(post.created_at).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })

  return (
    <Link to={`/posts/${post.id}`} className="post-card">
      <span className="category-pill">{post.category}</span>
      <h2>{post.title}</h2>
      <p className="post-card-excerpt">{excerpt(post.content)}</p>
      <div className="post-card-meta">
        {post.author} · {date}
      </div>
    </Link>
  )
}
