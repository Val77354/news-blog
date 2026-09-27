import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import PostForm from '../components/PostForm'
import { getPost, updatePost } from '../api/posts'

export default function EditPost() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [post, setPost] = useState(null)
  const [status, setStatus] = useState('loading')
  const [error, setError] = useState(null)

  useEffect(() => {
    getPost(id)
      .then((data) => {
        setPost(data)
        setStatus('ready')
      })
      .catch((err) => {
        setError(err.message)
        setStatus('error')
      })
  }, [id])

  async function handleSubmit(values) {
    await updatePost(id, values)
    navigate(`/posts/${id}`)
  }

  if (status === 'loading') {
    return (
      <div className="page container">
        <p className="state-message">Loading post…</p>
      </div>
    )
  }

  if (status === 'error') {
    return (
      <div className="page container">
        <p className="state-message error">Couldn't load post: {error}</p>
      </div>
    )
  }

  return (
    <div className="page container">
      <h1>Edit Post</h1>
      <PostForm
        initialValues={{
          title: post.title,
          content: post.content,
          author: post.author,
          category: post.category,
        }}
        onSubmit={handleSubmit}
        submitLabel="Save Changes"
      />
    </div>
  )
}
