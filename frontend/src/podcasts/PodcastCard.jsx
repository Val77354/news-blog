import { Link } from 'react-router-dom'
import { useInView } from '../hooks/useInView'
import { resolveImageUrl } from '../api/posts'
import { PODCAST_SOURCE_ICONS } from '../constants'
import { excerpt } from '../utils/text'
import './PodcastCard.css'

export default function PodcastCard({ podcast, index = 0, onDelete }) {
  const [ref, inView] = useInView()
  const cover = resolveImageUrl(podcast.cover_image_url)

  function handleDelete() {
    if (!window.confirm('Delete this podcast? This cannot be undone.')) return
    onDelete(podcast.id)
  }

  function handleMouseMove(e) {
    const rect = e.currentTarget.getBoundingClientRect()
    e.currentTarget.style.setProperty('--mouse-x', `${e.clientX - rect.left}px`)
    e.currentTarget.style.setProperty('--mouse-y', `${e.clientY - rect.top}px`)
  }

  return (
    <div
      className={`podcast-card${inView ? ' fade-up-item' : ''}`}
      style={inView ? { animationDelay: `${Math.min(index, 8) * 60}ms` } : { opacity: 0 }}
      ref={ref}
      onMouseMove={handleMouseMove}
    >
      {cover && (
        <img
          src={cover}
          alt=""
          className="podcast-card-image"
          onError={(e) => {
            e.currentTarget.style.display = 'none'
          }}
        />
      )}
      <span className="podcast-source-badge">
        {PODCAST_SOURCE_ICONS[podcast.source] ?? '🔗'} {podcast.source}
      </span>
      <h2>{podcast.title}</h2>
      <p className="podcast-card-host">{podcast.host}</p>
      <p className="podcast-card-description">{excerpt(podcast.description, 120)}</p>
      <div className="podcast-card-actions">
        <a
          href={podcast.external_url}
          target="_blank"
          rel="noopener noreferrer"
          className="btn btn-primary"
        >
          Listen on {podcast.source}
        </a>
        <Link to={`/podcasts/${podcast.id}/edit`} className="btn">
          Edit
        </Link>
        <button className="btn btn-danger" onClick={handleDelete} type="button">
          Delete
        </button>
      </div>
    </div>
  )
}
