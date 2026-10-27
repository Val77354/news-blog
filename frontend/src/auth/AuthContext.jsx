import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import * as authApi from '../api/auth'

const AuthContext = createContext(null)

// Knows whether the current visitor is logged in as admin.
// The real check always happens on the server; this only decides what to show.
export function AuthProvider({ children }) {
  const [isAdmin, setIsAdmin] = useState(false)
  const [ready, setReady] = useState(false)

  useEffect(() => {
    authApi
      .getAuthStatus()
      .then((s) => setIsAdmin(s.admin))
      .catch(() => setIsAdmin(false))
      .finally(() => setReady(true))
  }, [])

  const login = useCallback(async (password) => {
    await authApi.login(password)
    setIsAdmin(true)
  }, [])

  const logout = useCallback(async () => {
    await authApi.logout().catch(() => {})
    setIsAdmin(false)
  }, [])

  return <AuthContext.Provider value={{ isAdmin, ready, login, logout }}>{children}</AuthContext.Provider>
}

export function useAuth() {
  return useContext(AuthContext)
}

// Wrap admin-only pages: visitors are sent to the login page first.
export function AdminOnly({ children }) {
  const { isAdmin, ready } = useAuth()
  const location = useLocation()
  if (!ready) return null
  if (!isAdmin) return <Navigate to="/login" replace state={{ from: location.pathname }} />
  return children
}
