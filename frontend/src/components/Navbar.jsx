import { useEffect, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import './Navbar.css'

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false)
  const [query, setQuery] = useState(
    () => new URLSearchParams(window.location.search).get('q') || ''
  )
  const navigate = useNavigate()
  const location = useLocation()
  const onPodcasts = location.pathname === '/podcasts'

  useEffect(() => {
    function handleScroll() {
      setScrolled(window.scrollY > 24)
    }
    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  // Keep the box in sync with the destination's own ?q= whenever the route
  // itself changes (nav-link clicks, back/forward) — but not on every
  // keystroke, since typing changes the URL via the effect below too.
  useEffect(() => {
    const params = new URLSearchParams(location.search)
    setQuery(params.get('q') || '')
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.pathname])

  useEffect(() => {
    const timer = setTimeout(() => {
      const params = new URLSearchParams(window.location.search)
      const currentQuery = params.get('q') || ''
      if (query === currentQuery) return

      const currentPath = window.location.pathname
      if (currentPath === '/' || currentPath === '/podcasts') {
        if (query) params.set('q', query)
        else params.delete('q')
        navigate({ pathname: currentPath, search: params.toString() }, { replace: true })
      } else if (query) {
        navigate(`/?q=${encodeURIComponent(query)}`)
      }
    }, 300)
    return () => clearTimeout(timer)
  }, [query, navigate])

  return (
    <nav className={`navbar${scrolled ? ' navbar-scrolled' : ''}`}>
      <div className="navbar-inner">
        <Link to="/" className="navbar-brand">
          The Daily<span>Current</span>
        </Link>
        <div className="navbar-search">
          <svg viewBox="0 0 16 16" className="navbar-search-icon" aria-hidden="true">
            <circle cx="7" cy="7" r="5" fill="none" stroke="currentColor" strokeWidth="1.5" />
            <line x1="11" y1="11" x2="15" y2="15" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          </svg>
          <input
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={onPodcasts ? 'Search podcasts...' : 'Search articles...'}
            aria-label={onPodcasts ? 'Search podcasts' : 'Search articles'}
            className="navbar-search-input"
          />
          {query && (
            <button
              type="button"
              className="navbar-search-clear"
              onClick={() => setQuery('')}
              aria-label="Clear search"
            >
              ×
            </button>
          )}
        </div>
        <div className="navbar-actions">
          <Link to="/podcasts" className="btn">
            Podcasts
          </Link>
          <Link to="/posts/new" className="btn btn-primary">
            New Post
          </Link>
        </div>
      </div>
    </nav>
  )
}
