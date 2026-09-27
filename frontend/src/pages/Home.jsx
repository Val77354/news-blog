import { useEffect, useState } from 'react'
import { listPosts } from '../api/posts'
import PostCard from '../components/PostCard'
import './Home.css'

export default function Home() {
  const [posts, setPosts] = useState([])
  const [status, setStatus] = useState('loading')
  const [error, setError] = useState(null)

  useEffect(() => {
    listPosts()
      .then((data) => {
        setPosts(data)
        setStatus('ready')
      })
      .catch((err) => {
        setError(err.message)
        setStatus('error')
      })
  }, [])

  return (
    <div className="page container">
      <header className="hero">
        <h1>Stories worth your morning coffee.</h1>
        <p>Reporting on technology, business, science, and the world beyond your feed.</p>
      </header>

      {status === 'loading' && <p className="state-message">Loading posts…</p>}
      {status === 'error' && <p className="state-message error">Couldn't load posts: {error}</p>}
      {status === 'ready' && posts.length === 0 && (
        <p className="state-message">No posts yet — create the first one.</p>
      )}

      {status === 'ready' && posts.length > 0 && (
        <div className="post-grid">
          {posts.map((post) => (
            <PostCard key={post.id} post={post} />
          ))}
        </div>
      )}
    </div>
  )
}
