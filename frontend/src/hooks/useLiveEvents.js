import { useEffect, useRef, useState } from 'react'

const WS_BASE = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/^http/, 'ws')

export function useLiveEvents(onEvent) {
  const [connected, setConnected] = useState(false)
  const socketRef = useRef(null)

  useEffect(() => {
    const socket = new WebSocket(`${WS_BASE}/ws/events/`)
    socketRef.current = socket

    socket.onopen = () => setConnected(true)
    socket.onclose = () => setConnected(false)
    socket.onmessage = (message) => {
      try {
        const payload = JSON.parse(message.data)
        onEvent?.(payload)
      } catch {
        // ignore malformed messages
      }
    }

    return () => {
      socket.close()
    }
  }, [onEvent])

  return { connected }
}
