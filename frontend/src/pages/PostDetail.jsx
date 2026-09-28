import { useEffect, useState } from 'react'
import { useNavigate, useParams, useLocation, Link } from 'react-router-dom'
import { API_URL, getPost, deletePost } from '../api/posts'
import './PostDetail.css'

export default function PostDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const location = useLocation()
  const [post, setPost] = useState(null)
  const [status, setStatus] = useState('loading')
  const [error, setError] = useState(null)
  const [showToast, setShowToast] = useState(Boolean(location.state?.justSaved))
  const [toastMessage] = useState(location.state?.message || 'Saved!')

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

  useEffect(() => {
    if (!showToast) return
    const timer = setTimeout(() => setShowToast(false), 2500)
    return () => clearTimeout(timer)
  }, [showToast])

  useEffect(() => {
    if (location.state?.justSaved) {
      navigate(location.pathname, { replace: true, state: {} })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

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
      {showToast && (
        <div className="save-toast">
          <svg viewBox="0 0 16 16" className="save-toast-check">
            <polyline points="3,8 7,12 13,4" />
          </svg>
          {toastMessage}
        </div>
      )}
      {post.image_url && (
        <img src={`${API_URL}${post.image_url}`} alt="" className="post-detail-image" />
      )}
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
