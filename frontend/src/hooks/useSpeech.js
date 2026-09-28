import { useEffect, useState } from 'react'

const SUPPORTED = typeof window !== 'undefined' && 'speechSynthesis' in window

export function useSpeech(text) {
  const [speaking, setSpeaking] = useState(false)

  useEffect(() => {
    if (!SUPPORTED) return
    return () => {
      window.speechSynthesis.cancel()
    }
  }, [])

  // Chrome/Edge silently stall speechSynthesis after ~15s on a single long
  // utterance and often never fire `onend`. Pausing/resuming periodically
  // resets that internal timer and keeps long articles playing to the end.
  // This also reconciles `speaking` if the engine ever stops on its own
  // without firing onend/onerror.
  useEffect(() => {
    if (!SUPPORTED || !speaking) return
    const interval = setInterval(() => {
      if (!window.speechSynthesis.speaking) {
        setSpeaking(false)
        return
      }
      window.speechSynthesis.pause()
      window.speechSynthesis.resume()
    }, 10000)
    return () => clearInterval(interval)
  }, [speaking])

  function play() {
    if (!SUPPORTED || !text) return
    window.speechSynthesis.cancel()
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.onend = () => setSpeaking(false)
    utterance.onerror = () => setSpeaking(false)
    window.speechSynthesis.speak(utterance)
    setSpeaking(true)
  }

  function stop() {
    if (!SUPPORTED) return
    window.speechSynthesis.cancel()
    setSpeaking(false)
  }

  function toggle() {
    if (speaking) {
      stop()
    } else {
      play()
    }
  }

  return { speaking, toggle, supported: SUPPORTED }
}
