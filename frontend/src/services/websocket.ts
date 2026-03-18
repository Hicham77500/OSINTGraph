// ============================================================
// WebSocket Client — OsintGraph
// Socket.IO connection for real-time transform streaming
// ============================================================
import { io, Socket } from 'socket.io-client'

let socket: Socket | null = null

export function getSocket(): Socket {
  if (!socket) {
    socket = io('http://localhost:8000', {
      transports: ['websocket'],
      autoConnect: true,
      reconnection: true,
      reconnectionDelay: 1000,
    })

    socket.on('connect', () => {
      console.log('[WS] Connected to OsintGraph backend')
    })
    socket.on('disconnect', (reason) => {
      console.log('[WS] Disconnected:', reason)
    })
    socket.on('connect_error', (err) => {
      console.warn('[WS] Connection error:', err.message)
    })
  }
  return socket
}

export const wsClient = {
  on: (event: string, handler: (...args: any[]) => void) => {
    getSocket().on(event, handler)
  },
  off: (event: string, handler: (...args: any[]) => void) => {
    getSocket().off(event, handler)
  },
  emit: (event: string, data?: any) => {
    getSocket().emit(event, data)
  },
  disconnect: () => {
    socket?.disconnect()
    socket = null
  },
}
