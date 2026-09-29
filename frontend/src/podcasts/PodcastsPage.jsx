import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { listPodcasts, deletePodcast } from '../api/podcasts'
import PodcastCard from './PodcastCard'
import './PodcastsPage.css'

export default function PodcastsPage() {
  const [podcasts, setPodcasts] = useState([])
  const [status, setStatus] = useState('loading')
  const [error, setError] = useState(null)
  const [searchParams] = useSearchParams()
  const query = searchParams.get('q') || ''

  useEffect(() => {
    let ignore = false
    setStatus('loading')
    listPodcasts({ q: query })
      .then((data) => {
        if (!ignore) {
          setPodcasts(data)
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
  }, [query])

  async function handleDelete(id) {
    try {
      await deletePodcast(id)
      setPodcasts((current) => current.filter((p) => p.id !== id))
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="page container">
      <header className="podcasts-header">
        <div>
          <h1>Listen</h1>
          <p>Podcasts and shows from The DailyCurrent and other networks, all in one place.</p>
        </div>
        <Link to="/podcasts/new" className="btn btn-primary">
          Add Podcast
        </Link>
      </header>

      {status === 'loading' && (
        <div className="podcast-grid">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="podcast-skeleton-card" />
          ))}
        </div>
      )}
      {status === 'error' && <p className="state-message error">Couldn't load podcasts: {error}</p>}
      {status === 'ready' && podcasts.length === 0 && (
        <p className="state-message">
          {query ? `No podcasts match "${query}".` : 'No podcasts yet — add the first one.'}
        </p>
      )}
      {status === 'ready' && podcasts.length > 0 && (
        <div className="podcast-grid">
          {podcasts.map((podcast, i) => (
            <PodcastCard key={podcast.id} podcast={podcast} index={i} onDelete={handleDelete} />
          ))}
        </div>
      )}
    </div>
  )
}
