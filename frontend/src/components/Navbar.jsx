import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import './Navbar.css'

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    function handleScroll() {
      setScrolled(window.scrollY > 24)
    }
    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <nav className={`navbar${scrolled ? ' navbar-scrolled' : ''}`}>
      <div className="navbar-inner">
        <Link to="/" className="navbar-brand">
          The Daily<span>Current</span>
        </Link>
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
