import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

export const api = axios.create({
  baseURL: API_URL,
})

export function extractListData<T>(data: unknown): T[] {
  if (Array.isArray(data)) {
    return data as T[]
  }

  if (
    data &&
    typeof data === 'object' &&
    'results' in data &&
    Array.isArray((data as { results?: unknown }).results)
  ) {
    return (data as { results: T[] }).results
  }

  return []
}

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth APIs
export const authAPI = {
  login: (username: string, password: string) =>
    api.post('/token/', { username, password }),
  register: (data: {
    username: string
    email: string
    password: string
    password_confirm: string
  }) =>
    api.post('/accounts/register/', data),
  getProfile: () => api.get('/accounts/profile/'),
  updateProfile: (data: any) => api.patch('/accounts/profile/', data),
}

// Links API
export const linksAPI = {
  getList: (params?: any) => api.get('/links/', { params }),
  create: (data: { original_url: string; title?: string; custom_slug?: string }) =>
    api.post('/links/', data),
  getOne: (id: number) => api.get(`/links/${id}/`),
  update: (id: number, data: any) => api.patch(`/links/${id}/`, data),
  delete: (id: number) => api.delete(`/links/${id}/`),
  getQR: (shortCode: string) => `${API_URL}/links/${shortCode}/qr/`,
}

// Analytics API
export const analyticsAPI = {
  getSummary: () => api.get('/analytics/summary/'),
  getLinkAnalytics: (id: number) => api.get(`/analytics/link/${id}/`),
  getDeviceAccess: (linkId: number) => api.get(`/analytics/link/${linkId}/devices/`),
  getIPLocations: (linkId: number) => api.get(`/analytics/link/${linkId}/ip-locations/`),
  getIPStats: (linkId: number) => api.get(`/analytics/link/${linkId}/ip-stats/`),
}
