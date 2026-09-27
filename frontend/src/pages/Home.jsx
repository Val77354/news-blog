import { useEffect, useState } from 'react'
import { listPosts } from '../api/posts'
import PostCard from '../components/PostCard'
import CategoryTabs from '../components/CategoryTabs'
import CountryFilter from '../components/CountryFilter'
import './Home.css'

export default function Home() {
  const [posts, setPosts] = useState([])
  const [status, setStatus] = useState('loading')
  const [error, setError] = useState(null)
  const [activeCategory, setActiveCategory] = useState(null)
  const [selectedCountries, setSelectedCountries] = useState([])

  useEffect(() => {
    setStatus('loading')
    listPosts({ category: activeCategory, countries: selectedCountries })
      .then((data) => {
        setPosts(data)
        setStatus('ready')
      })
      .catch((err) => {
        setError(err.message)
        setStatus('error')
      })
  }, [activeCategory, selectedCountries])

  return (
    <div className="page container">
      <header className="hero">
        <h1>Stories worth your morning coffee.</h1>
        <p>Reporting on technology, business, science, and the world beyond your feed.</p>
      </header>

      <CategoryTabs active={activeCategory} onChange={setActiveCategory} />
      <CountryFilter selected={selectedCountries} onChange={setSelectedCountries} />

      {status === 'loading' && <p className="state-message">Loading posts…</p>}
      {status === 'error' && <p className="state-message error">Couldn't load posts: {error}</p>}
      {status === 'ready' && posts.length === 0 && (
        <p className="state-message">No posts match these filters.</p>
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
