import { useNavigate } from 'react-router-dom'
import { createPodcast } from '../api/podcasts'
import PodcastForm from './PodcastForm'

export default function NewPodcast() {
  const navigate = useNavigate()

  async function handleSubmit(values) {
    await createPodcast(values)
    navigate('/podcasts')
  }

  return (
    <div className="page container">
      <h1>Add Podcast</h1>
      <PodcastForm onSubmit={handleSubmit} submitLabel="Add Podcast" />
    </div>
  )
}
