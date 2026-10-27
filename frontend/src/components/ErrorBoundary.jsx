import { Component } from 'react'

// If a page crashes, show a friendly message instead of a blank screen.
export default class ErrorBoundary extends Component {
  state = { failed: false }

  static getDerivedStateFromError() {
    return { failed: true }
  }

  componentDidCatch(error, info) {
    console.error('Page crashed:', error, info.componentStack)
  }

  render() {
    if (!this.state.failed) return this.props.children
    return (
      <div className="page container">
        <h1>Something went wrong</h1>
        <p className="state-message">This page hit an unexpected problem. Going back to the home page usually fixes it.</p>
        <a className="btn btn-primary" href="/">
          Back to home
        </a>
      </div>
    )
  }
}
