import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { listPosts } from '../api/posts'
import PostCard from '../components/PostCard'
import CategoryTabs from '../components/CategoryTabs'
import CountryFilter from '../components/CountryFilter'
import ListenBar from '../components/ListenBar'
import './Home.css'

export default function Home() {
  const [posts, setPosts] = useState([])
  const [status, setStatus] = useState('loading')
  const [error, setError] = useState(null)
  const [searchParams, setSearchParams] = useSearchParams()

  const activeCategory = searchParams.get('category')
  const countriesParam = searchParams.get('countries')
  const selectedCountries = countriesParam ? countriesParam.split(',') : []

  function setActiveCategory(value) {
    const next = new URLSearchParams(searchParams)
    if (value) next.set('category', value)
    else next.delete('category')
    setSearchParams(next)
  }

  function setSelectedCountries(values) {
    const next = new URLSearchParams(searchParams)
    if (values.length > 0) next.set('countries', values.join(','))
    else next.delete('countries')
    setSearchParams(next)
  }

  useEffect(() => {
    let ignore = false
    setStatus('loading')
    listPosts({ category: activeCategory, countries: selectedCountries })
      .then((data) => {
        if (!ignore) {
          setPosts(data)
          setStatus('ready')
        }
      })
      .catch((err) => {
        if (!ignore) {
          setError(err.message)
          setStatus('error')
        }
      })
    return () => {
      ignore = true
    }
  }, [activeCategory, countriesParam])

  return (
    <div className="page container">
      <header className="hero">
        <div className="hero-backdrop" aria-hidden="true" />
        <h1 className="hero-title">
          {'Stories worth your morning coffee.'.split(' ').map((word, i) => (
            <span key={i} className="hero-word" style={{ animationDelay: `${i * 80}ms` }}>
              {word}&nbsp;
            </span>
          ))}
        </h1>
        <span className="hero-underline" />
        <p>Reporting on technology, business, science, and the world beyond your feed.</p>
      </header>

      <ListenBar />

      <CategoryTabs active={activeCategory} onChange={setActiveCategory} />
      <CountryFilter selected={selectedCountries} onChange={setSelectedCountries} />

      {status === 'loading' && (
        <div className="post-grid">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="skeleton-card" />
          ))}
        </div>
      )}
      {status === 'error' && <p className="state-message error">Couldn't load posts: {error}</p>}
      {status === 'ready' && posts.length === 0 && (
        <p className="state-message">No posts match these filters.</p>
      )}

      {status === 'ready' && posts.length > 0 && (
        <div className="post-grid">
          {posts.map((post, index) => (
            <PostCard key={post.id} post={post} index={index} />
          ))}
        </div>
      )}
    </div>
  )
}
