import { useEffect, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { listPosts } from '../api/posts'
import './Ticker.css'

export default function Ticker() {
  const [posts, setPosts] = useState([])
  const { pathname } = useLocation()

  useEffect(() => {
    listPosts()
      .then((data) => setPosts(data.slice(0, 5)))
      .catch(() => setPosts([]))
  }, [pathname])

  if (posts.length === 0) return null

  return (
    <div className="ticker">
      <span className="ticker-label">Breaking</span>
      <div className="ticker-track">
        <div className="ticker-content">
          {posts.map((post) => (
            <Link key={post.id} to={`/posts/${post.id}`} className="ticker-item">
              {post.title}
            </Link>
          ))}
        </div>
        <div className="ticker-content" aria-hidden="true">
          {posts.map((post) => (
            <span key={post.id} className="ticker-item">
              {post.title}
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}
