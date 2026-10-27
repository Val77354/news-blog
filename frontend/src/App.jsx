import { Routes, Route } from 'react-router-dom'
import Backdrop from './components/Backdrop'
import Ticker from './components/Ticker'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import Home from './pages/Home'
import PostDetail from './pages/PostDetail'
import NewPost from './pages/NewPost'
import EditPost from './pages/EditPost'
import Login from './pages/Login'
import PodcastsPage from './podcasts/PodcastsPage'
import NewPodcast from './podcasts/NewPodcast'
import EditPodcast from './podcasts/EditPodcast'
import { AuthProvider, AdminOnly } from './auth/AuthContext'

export default function App() {
  return (
    <AuthProvider>
      <Backdrop />
      <Ticker />
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/posts/new" element={<AdminOnly><NewPost /></AdminOnly>} />
        <Route path="/posts/:id" element={<PostDetail />} />
        <Route path="/posts/:id/edit" element={<AdminOnly><EditPost /></AdminOnly>} />
        <Route path="/podcasts" element={<PodcastsPage />} />
        <Route path="/podcasts/new" element={<AdminOnly><NewPodcast /></AdminOnly>} />
        <Route path="/podcasts/:id/edit" element={<AdminOnly><EditPodcast /></AdminOnly>} />
      </Routes>
      <Footer />
    </AuthProvider>
  )
}
