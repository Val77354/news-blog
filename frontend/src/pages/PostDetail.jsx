import { useEffect, useState } from 'react'
import { useNavigate, useParams, Link } from 'react-router-dom'
import { getPost, deletePost } from '../api/posts'
import './PostDetail.css'

export default function PostDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [post, setPost] = useState(null)
  const [status, setStatus] = useState('loading')
  const [error, setError] = useState(null)

  useEffect(() => {
    setStatus('loading')
    getPost(id)
      .then((data) => {
        setPost(data)
        setStatus('ready')
      })
      .catch((err) => {
        setError(err.message)
        setStatus('error')
      })
  }, [id])

  async function handleDelete() {
    if (!window.confirm('Delete this post? This cannot be undone.')) return
    try {
      await deletePost(id)
      navigate('/')
    } catch (err) {
      setError(err.message)
    }
  }

  if (status === 'loading') {
    return (
      <div className="page container">
        <p className="state-message">Loading post…</p>
      </div>
    )
  }

  if (status === 'error') {
    return (
      <div className="page container">
        <p className="state-message error">Couldn't load post: {error}</p>
      </div>
    )
  }

  const date = new Date(post.created_at).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })

  return (
    <div className="page container post-detail">
      <div className="badge-row">
        <span className="category-pill">{post.category}</span>
        <span className="country-badge">{post.country}</span>
      </div>
      <h1>{post.title}</h1>
      <div className="post-detail-meta state-message">
        {post.author} · {date}
      </div>
      <p className="post-detail-body">{post.content}</p>
      <div className="post-detail-actions">
        <Link to={`/posts/${post.id}/edit`} className="btn">
          Edit
        </Link>
        <button className="btn btn-danger" onClick={handleDelete}>
          Delete
        </button>
      </div>
      {error && <p className="state-message error">{error}</p>}
    </div>
  )
}
