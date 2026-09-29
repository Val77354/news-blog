import { Link } from 'react-router-dom'
import { CATEGORIES, COUNTRIES, COUNTRY_FLAGS } from '../constants'
import './Footer.css'

export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="site-footer-inner container">
        <div className="site-footer-grid">
          <div className="site-footer-brand">
            <span className="site-footer-brand-name">
              The Daily<span>Current</span>
            </span>
            <p>
              Independent reporting on technology, business, science, and the world beyond your
              feed.
            </p>
          </div>
          <div className="site-footer-column">
            <h3>Categories</h3>
            <ul>
              {CATEGORIES.map((c) => (
                <li key={c}>
                  <Link to={`/?category=${encodeURIComponent(c)}`}>{c}</Link>
                </li>
              ))}
            </ul>
          </div>
          <div className="site-footer-column site-footer-countries">
            <h3>Countries</h3>
            <ul>
              {COUNTRIES.map((c) => (
                <li key={c}>
                  <Link to={`/?countries=${encodeURIComponent(c)}`}>
                    {COUNTRY_FLAGS[c]} {c}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
          <div className="site-footer-column">
            <h3>Explore</h3>
            <ul>
              <li>
                <Link to="/">Home</Link>
              </li>
              <li>
                <Link to="/podcasts">Podcasts</Link>
              </li>
              <li>
                <Link to="/posts/new">New Post</Link>
              </li>
            </ul>
          </div>
        </div>
        <div className="site-footer-bottom">
          <span>© 2026 The DailyCurrent. Fictional demo publication, built for portfolio purposes only.</span>
          <span>Built with FastAPI, SQLAlchemy &amp; React.</span>
        </div>
      </div>
    </footer>
  )
}
