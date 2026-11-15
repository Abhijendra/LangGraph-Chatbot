const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
const TOKEN_KEY = 'token'

export class AuthError extends Error {}

export const getToken = () => sessionStorage.getItem(TOKEN_KEY)
export const clearToken = () => sessionStorage.removeItem(TOKEN_KEY)

export async function login(employeeId: number, password: string): Promise<void> {
  const res = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ employee_id: employeeId, password }),
  })
  if (res.status === 401) throw new Error('Invalid employee ID or password')
  if (!res.ok) throw new Error(`Login failed (${res.status})`)
  const data = await res.json()
  sessionStorage.setItem(TOKEN_KEY, data.access_token)
}

export async function sendQuery(sessionId: string, query: string): Promise<string> {
  const res = await fetch(`${API_URL}/chat/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${getToken()}`,
    },
    body: JSON.stringify({ session_id: sessionId, query }),
  })
  if (res.status === 401) {
    clearToken()
    throw new AuthError('Session expired. Please log in again.')
  }
  if (!res.ok) throw new Error(`Request failed (${res.status})`)
  const data = await res.json()
  return data.response
}
