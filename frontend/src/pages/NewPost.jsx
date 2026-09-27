import { useNavigate } from 'react-router-dom'
import PostForm from '../components/PostForm'
import { createPost } from '../api/posts'

export default function NewPost() {
  const navigate = useNavigate()

  async function handleSubmit(values) {
    const post = await createPost(values)
    navigate(`/posts/${post.id}`)
  }

  return (
    <div className="page container">
      <h1>New Post</h1>
      <PostForm onSubmit={handleSubmit} submitLabel="Publish" />
    </div>
  )
}
