import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { getPodcast, updatePodcast } from '../api/podcasts'
import PodcastForm from './PodcastForm'

export default function EditPodcast() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [podcast, setPodcast] = useState(null)
  const [status, setStatus] = useState('loading')
  const [error, setError] = useState(null)

  useEffect(() => {
    getPodcast(id)
      .then((data) => {
        setPodcast(data)
        setStatus('ready')
      })
      .catch((err) => {
        setError(err.message)
        setStatus('error')
      })
  }, [id])

  async function handleSubmit(values) {
    await updatePodcast(id, values)
    navigate('/podcasts')
  }

  if (status === 'loading') {
    return (
      <div className="page container">
        <p className="state-message">Loading podcast…</p>
      </div>
    )
  }

  if (status === 'error') {
    return (
      <div className="page container">
        <p className="state-message error">Couldn't load podcast: {error}</p>
      </div>
    )
  }

  return (
    <div className="page container">
      <h1>Edit Podcast</h1>
      <PodcastForm
        initialValues={{
          title: podcast.title,
          host: podcast.host,
          description: podcast.description,
          cover_image_url: podcast.cover_image_url,
          source: podcast.source,
          external_url: podcast.external_url,
        }}
        onSubmit={handleSubmit}
        submitLabel="Save Changes"
      />
    </div>
  )
}
