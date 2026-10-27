import { useEffect, useState } from 'react'
import { useNavigate, useParams, useLocation, Link } from 'react-router-dom'
import { resolveImageUrl, getPost, deletePost, listPosts, recordView } from '../api/posts'
import { COUNTRY_FLAGS } from '../constants'
import { getReadTime, formatViews, displayDate } from '../utils/postMeta'
import './PostDetail.css'
import { useAuth } from '../auth/AuthContext'

export default function PostDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { isAdmin } = useAuth()
  const location = useLocation()
  const [post, setPost] = useState(null)
  const [status, setStatus] = useState('loading')
  const [error, setError] = useState(null)
  const [showToast, setShowToast] = useState(Boolean(location.state?.justSaved))
  const [toastMessage] = useState(location.state?.message || 'Saved!')
  const [relatedPosts, setRelatedPosts] = useState([])
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    window.scrollTo(0, 0)
  }, [id])

  useEffect(() => {
    setStatus('loading')
    getPost(id)
      .then((data) => {
        setPost(data)
        setStatus('ready')
        // Old number links (/posts/12) switch to the readable address.
        if (/^\d+$/.test(id)) navigate(`/posts/${data.slug}`, { replace: true, state: location.state })
      })
      .catch((err) => {
        setError(err.message)
        setStatus('error')
      })
  }, [id])

  // Count one real view per visit (the server ignores repeats and the admin).
  const postId = post?.id
  useEffect(() => {
    if (!postId) return
    recordView(postId)
      .then(({ view_count }) => setPost((p) => (p && p.id === postId ? { ...p, view_count } : p)))
      .catch(() => {})
  }, [postId])

  useEffect(() => {
    if (!post) return
    let ignore = false
    listPosts()
      .then((all) => {
        if (ignore) return
        const related = all
          .filter((p) => p.id !== post.id && (p.category === post.category || p.country === post.country))
          .slice(0, 4)
        setRelatedPosts(related)
      })
      .catch(() => {
        // related posts are a nice-to-have; failing silently keeps the page usable
      })
    return () => {
      ignore = true
    }
  }, [post])

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

  function handleCopyLink() {
    navigator.clipboard.writeText(window.location.href).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }).catch(() => {
      setError('Could not copy link')
    })
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

  const date = displayDate(post, { year: 'numeric', month: 'long', day: 'numeric' })
  const shareText = encodeURIComponent(post.title)
  const shareUrl = encodeURIComponent(window.location.href)

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
        <img
          src={resolveImageUrl(post.image_url)}
          alt=""
          className="post-detail-image"
          onError={(e) => {
            e.currentTarget.style.display = 'none'
          }}
        />
      )}
      <div className="badge-row">
        {post.status === 'draft' && <span className="draft-badge">Draft — only you can see this</span>}
        <span className="category-pill">{post.category}</span>
        <span className="country-badge">
          {COUNTRY_FLAGS[post.country]} {post.country}
        </span>
      </div>
      <h1>{post.title}</h1>
      <div className="post-detail-meta state-message">
        {post.author} · {date}
      </div>
      <p className="post-detail-body">{post.content}</p>

      <div className="post-detail-extras">
        <div className="post-detail-stats">
          <span>{getReadTime(post.content)}</span>
          <span>{formatViews(post.view_count)}</span>
        </div>
        <div className="post-detail-share">
          <span className="post-detail-share-label">Share:</span>
          <button type="button" className="btn" onClick={handleCopyLink}>
            {copied ? 'Copied!' : 'Copy link'}
          </button>
          <a
            className="btn"
            href={`https://twitter.com/intent/tweet?text=${shareText}&url=${shareUrl}`}
            target="_blank"
            rel="noopener noreferrer"
          >
            X
          </a>
          <a
            className="btn"
            href={`https://www.facebook.com/sharer/sharer.php?u=${shareUrl}`}
            target="_blank"
            rel="noopener noreferrer"
          >
            Facebook
          </a>
          <a className="btn" href={`mailto:?subject=${shareText}&body=${shareUrl}`}>
            Email
          </a>
        </div>
      </div>

      {relatedPosts.length > 0 && (
        <div className="related-posts">
          <h2 className="related-posts-title">More like this</h2>
          <div className="related-posts-grid">
            {relatedPosts.map((related) => (
              <Link key={related.id} to={`/posts/${related.slug}`} className="related-post-card">
                {related.image_url && (
                  <img src={resolveImageUrl(related.image_url)} alt="" className="related-post-image" />
                )}
                <span className="related-post-title">{related.title}</span>
              </Link>
            ))}
          </div>
        </div>
      )}

      {isAdmin && (
        <div className="post-detail-actions">
          <Link to={`/posts/${post.id}/edit`} className="btn">
            Edit
          </Link>
          <button className="btn btn-danger" onClick={handleDelete}>
            Delete
          </button>
        </div>
      )}
      {error && <p className="state-message error">{error}</p>}
    </div>
  )
}
