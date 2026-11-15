import { useState } from 'react'
import { clearToken, getToken } from './api'
import Chat from './Chat'
import Login from './Login'

export default function App() {
  const [loggedIn, setLoggedIn] = useState(() => !!getToken())
  const [notice, setNotice] = useState('')

  function logout(message = '') {
    clearToken()
    setNotice(message)
    setLoggedIn(false)
  }

  return loggedIn ? (
    <Chat onLogout={() => logout()} onExpired={() => logout('Session expired. Please log in again.')} />
  ) : (
    <Login notice={notice} onSuccess={() => { setNotice(''); setLoggedIn(true) }} />
  )
}
