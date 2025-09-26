import axios from 'axios'

// Configuración Axios
const API_BASE_URL = 'http://127.0.0.1:8000/api'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor para agregar token de autorización
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('adminToken')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Interceptor para manejar respuestas de error
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('adminToken')
      window.location.href = '/admin/login'
    }
    return Promise.reject(error)
  }
)

export const contestAPI = {
  // Endpoints públicos
  getStats() {
    return apiClient.get('/stats/')
  },
  
  registerParticipant(data) {
    return apiClient.post('/register/', data)
  },
  
  verifyEmail(token) {
    return apiClient.post('/verify-email/', { token })
  },
  
  createPassword(data) {
    return apiClient.post('/create-password/', data)
  },
  
  // Endpoints de administración
  adminLogin(credentials) {
    return apiClient.post('/admin/login/', credentials)
  },
  
  getParticipants(filters = {}) {
    const params = new URLSearchParams()
    if (filters.search) params.append('search', filters.search)
    if (filters.status) params.append('status', filters.status)
    
    return apiClient.get(`/admin/participants/?${params}`)
  },
  
  selectWinner(count = 1) {
    return apiClient.post('/admin/select-winner/', { count })
  },
  
  getWinners() {
    return apiClient.get('/admin/winners/')
  },
  
  notifyWinners() {
    return apiClient.post('/admin/notify-winners/')
  },
  
  resendVerification(email) {
    return apiClient.post('/admin/resend-verification/', { email })
  }
}

export default contestAPI