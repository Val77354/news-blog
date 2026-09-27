import { Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import PostDetail from './pages/PostDetail'
import NewPost from './pages/NewPost'
import EditPost from './pages/EditPost'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/posts/new" element={<NewPost />} />
      <Route path="/posts/:id" element={<PostDetail />} />
      <Route path="/posts/:id/edit" element={<EditPost />} />
    </Routes>
  )
}
