import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

const SECONDS = 4

// Any unknown address: explain briefly, then go to the home page automatically.
export default function NotFound() {
  const navigate = useNavigate()
  const [left, setLeft] = useState(SECONDS)

  useEffect(() => {
    if (left === 0) {
      navigate('/', { replace: true })
      return
    }
    const timer = setTimeout(() => setLeft((n) => n - 1), 1000)
    return () => clearTimeout(timer)
  }, [left, navigate])

  return (
    <div className="page container">
      <h1>Page not found</h1>
      <p className="state-message">
        This page doesn't exist. Taking you to the home page in {left}…
      </p>
      <Link to="/" replace className="btn btn-primary">
        Go now
      </Link>
    </div>
  )
}
