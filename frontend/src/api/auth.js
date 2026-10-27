import { apiFetch } from './client'

export const login = (password) => apiFetch('/auth/login', { method: 'POST', json: { password } })
export const logout = () => apiFetch('/auth/logout', { method: 'POST' })
export const getAuthStatus = () => apiFetch('/auth/me')
