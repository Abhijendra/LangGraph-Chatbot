import { useEffect, useRef, useState, type FormEvent } from 'react'
import { AuthError, sendQuery } from './api'

type Message = { role: 'user' | 'bot' | 'error'; text: string }

export default function Chat({ onLogout, onExpired }: { onLogout: () => void; onExpired: () => void }) {
  const [sessionId, setSessionId] = useState(() => crypto.randomUUID())
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  function newChat() {
    setSessionId(crypto.randomUUID())
    setMessages([])
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const text = input.trim()
    if (!text || loading) return
    setInput('')
    setMessages((m) => [...m, { role: 'user', text }])
    setLoading(true)
    try {
      const reply = await sendQuery(sessionId, text)
      setMessages((m) => [...m, { role: 'bot', text: reply }])
    } catch (err) {
      if (err instanceof AuthError) return onExpired()
      const msg = err instanceof TypeError ? 'Cannot reach the server' : (err as Error).message
      setMessages((m) => [...m, { role: 'error', text: msg }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card chat">
      <header>
        <h1>HR Chatbot</h1>
        <div>
          <button className="link" onClick={newChat}>New chat</button>
          <button className="link" onClick={onLogout}>Log out</button>
        </div>
      </header>
      <div className="messages">
        {messages.length === 0 && <p className="hint">Ask me anything about HR.</p>}
        {messages.map((m, i) => (
          <div key={i} className={`msg ${m.role}`}>{m.text}</div>
        ))}
        {loading && <div className="msg bot thinking">Thinking...</div>}
        <div ref={bottomRef} />
      </div>
      <form onSubmit={handleSubmit}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your question..."
          maxLength={4000}
          autoFocus
        />
        <button disabled={loading || !input.trim()}>Send</button>
      </form>
    </div>
  )
}
