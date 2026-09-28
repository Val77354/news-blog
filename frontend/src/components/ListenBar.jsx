import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { listPosts } from '../api/posts'
import { useSpeech } from '../hooks/useSpeech'
import './ListenBar.css'

export default function ListenBar() {
  const [latest, setLatest] = useState(null)

  useEffect(() => {
    listPosts()
      .then((data) => setLatest(data[0] || null))
      .catch(() => setLatest(null))
  }, [])

  const text = latest ? `${latest.title}. ${latest.content}` : ''
  const { speaking, toggle } = useSpeech(text)

  if (!latest) return null

  return (
    <div className="listen-bar">
      <button
        type="button"
        className={`listen-play${speaking ? ' listen-play-active' : ''}`}
        onClick={toggle}
        aria-label={speaking ? 'Stop listening' : 'Listen to this story'}
      >
        {speaking ? (
          <span className="listen-equalizer" aria-hidden="true">
            <span />
            <span />
            <span />
          </span>
        ) : (
          <svg viewBox="0 0 16 16" className="listen-play-icon">
            <polygon points="4,3 13,8 4,13" />
          </svg>
        )}
      </button>
      <div className="listen-copy">
        <span className="listen-label">Listen</span>
        <Link to={`/posts/${latest.id}`} className="listen-title">
          {latest.title}
        </Link>
      </div>
    </div>
  )
}
