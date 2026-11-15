import { useState, type FormEvent } from 'react'
import { login } from './api'

export default function Login({ onSuccess, notice }: { onSuccess: () => void; notice?: string }) {
  const [employeeId, setEmployeeId] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(notice ?? '')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(Number(employeeId), password)
      onSuccess()
    } catch (err) {
      setError(err instanceof TypeError ? 'Cannot reach the server' : (err as Error).message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <form className="card login" onSubmit={handleSubmit}>
      <h1>HR Chatbot</h1>
      <input
        type="number"
        placeholder="Employee ID"
        value={employeeId}
        onChange={(e) => setEmployeeId(e.target.value)}
        required
        autoFocus
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
      />
      {error && <p className="error">{error}</p>}
      <button disabled={loading}>{loading ? 'Signing in...' : 'Sign in'}</button>
    </form>
  )
}
