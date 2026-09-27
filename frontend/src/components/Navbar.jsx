import { Link } from 'react-router-dom'
import './Navbar.css'

export default function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <Link to="/" className="navbar-brand">
          The Daily<span>Wire</span>
        </Link>
        <Link to="/posts/new" className="btn btn-primary">
          New Post
        </Link>
      </div>
    </nav>
  )
}
