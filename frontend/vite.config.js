import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// During `npm run dev`, send API calls to the backend on port 8000, so the
// site and the API share one address just like in production.
const backend = 'http://localhost:8000'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': backend,
      '/feed.xml': backend,
      '/sitemap.xml': backend,
    },
  },
})
