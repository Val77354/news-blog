import { Routes, Route } from 'react-router-dom'
import Backdrop from './components/Backdrop'
import Ticker from './components/Ticker'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import Home from './pages/Home'
import PostDetail from './pages/PostDetail'
import NewPost from './pages/NewPost'
import EditPost from './pages/EditPost'
import PodcastsPage from './podcasts/PodcastsPage'
import NewPodcast from './podcasts/NewPodcast'
import EditPodcast from './podcasts/EditPodcast'

export default function App() {
  return (
    <>
      <Backdrop />
      <Ticker />
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/posts/new" element={<NewPost />} />
        <Route path="/posts/:id" element={<PostDetail />} />
        <Route path="/posts/:id/edit" element={<EditPost />} />
        <Route path="/podcasts" element={<PodcastsPage />} />
        <Route path="/podcasts/new" element={<NewPodcast />} />
        <Route path="/podcasts/:id/edit" element={<EditPodcast />} />
      </Routes>
      <Footer />
    </>
  )
}
