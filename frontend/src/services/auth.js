const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
const TOKEN_KEY = 'crds_access_token'
const REFRESH_KEY = 'crds_refresh_token'

export function getAccessToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function getRefreshToken() {
  return localStorage.getItem(REFRESH_KEY)
}

export function setTokens({ access, refresh }) {
  if (access) localStorage.setItem(TOKEN_KEY, access)
  if (refresh) localStorage.setItem(REFRESH_KEY, refresh)
}

export function clearTokens() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(REFRESH_KEY)
}

export function isAuthenticated() {
  return Boolean(getAccessToken())
}

export async function login(username, password) {
  const response = await fetch(`${API_BASE}/api/auth/login/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new Error(error.detail || 'Login failed')
  }
  const data = await response.json()
  setTokens({ access: data.access, refresh: data.refresh })
  return data
}

export async function register(username, email, password) {
  const response = await fetch(`${API_BASE}/api/auth/register/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, email, password }),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new Error(error.detail || error.username?.[0] || 'Registration failed')
  }
  return response.json()
}

export async function fetchCurrentUser() {
  const token = getAccessToken()
  if (!token) return null
  const response = await fetch(`${API_BASE}/api/auth/me/`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!response.ok) {
    clearTokens()
    return null
  }
  return response.json()
}

export async function refreshAccessToken() {
  const refresh = getRefreshToken()
  if (!refresh) return false
  const response = await fetch(`${API_BASE}/api/auth/login/refresh/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh }),
  })
  if (!response.ok) {
    clearTokens()
    return false
  }
  const data = await response.json()
  setTokens({ access: data.access })
  return true
}
