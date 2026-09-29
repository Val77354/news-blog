import { Link } from 'react-router-dom'
import { resolveImageUrl } from '../api/posts'
import { PODCAST_SOURCE_ICONS } from '../constants'
import './PodcastCard.css'

function excerpt(text, length = 120) {
  const flat = text.replace(/\s+/g, ' ').trim()
  return flat.length > length ? `${flat.slice(0, length)}…` : flat
}

export default function PodcastCard({ podcast, onDelete }) {
  const cover = resolveImageUrl(podcast.cover_image_url)

  function handleDelete() {
    if (!window.confirm('Delete this podcast? This cannot be undone.')) return
    onDelete(podcast.id)
  }

  return (
    <div className="podcast-card">
      {cover && <img src={cover} alt="" className="podcast-card-image" />}
      <span className="podcast-source-badge">
        {PODCAST_SOURCE_ICONS[podcast.source] ?? '🔗'} {podcast.source}
      </span>
      <h2>{podcast.title}</h2>
      <p className="podcast-card-host">{podcast.host}</p>
      <p className="podcast-card-description">{excerpt(podcast.description)}</p>
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
