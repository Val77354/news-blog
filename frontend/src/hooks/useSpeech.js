import { useEffect, useRef, useState } from 'react'

export function useSpeech(text) {
  const [speaking, setSpeaking] = useState(false)
  const utteranceRef = useRef(null)

  useEffect(() => {
    return () => {
      window.speechSynthesis.cancel()
    }
  }, [])

  function play() {
    if (!text) return
    window.speechSynthesis.cancel()
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.onend = () => setSpeaking(false)
    utterance.onerror = () => setSpeaking(false)
    utteranceRef.current = utterance
    window.speechSynthesis.speak(utterance)
    setSpeaking(true)
  }

  function stop() {
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

  return { speaking, toggle }
}
