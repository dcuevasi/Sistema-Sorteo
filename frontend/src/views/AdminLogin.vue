<template>
  <div class="admin-login-container">
    <div class="login-card">
      <div class="card-header">
        <h1>Panel de Administrador</h1>
        <p>Acceso exclusivo para administradores del sorteo</p>
      </div>

      <form @submit.prevent="login" class="login-form">
        <div class="form-group">
          <label for="username">Usuario</label>
          <input
            id="username"
            v-model="form.username"
            type="text"
            required
            placeholder="Ingresa tu usuario"
            :disabled="loading"
            autocomplete="username"
          />
          <span v-if="errors.username" class="error">{{ errors.username[0] }}</span>
        </div>

        <div class="form-group">
          <label for="password">Contraseña</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            required
            placeholder="Ingresa tu contraseña"
            :disabled="loading"
            autocomplete="current-password"
          />
          <span v-if="errors.password" class="error">{{ errors.password[0] }}</span>
        </div>

        <button 
          type="submit" 
          class="login-button"
          :disabled="loading"
        >
          {{ loading ? 'Iniciando sesión...' : 'Iniciar Sesión' }}
        </button>
      </form>

      <div v-if="generalError" class="error-message">
        <div class="error-icon">⚠️</div>
        <p>{{ generalError }}</p>
      </div>

      <div class="back-link">
        <router-link to="/" class="back-text">
          ← Volver al sitio anterior
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { contestAPI } from '../services/api.js'

export default {
  name: 'AdminLogin',
  setup() {
    const router = useRouter()
    
    const form = reactive({
      username: '',
      password: ''
    })
    
    const loading = ref(false)
    const errors = ref({})
    const generalError = ref('')

    const login = async () => {
      loading.value = true
      errors.value = {}
      generalError.value = ''

      try {
        const response = await contestAPI.adminLogin(form)       
        localStorage.setItem('adminToken', response.data.access_token)
        localStorage.setItem('adminUser', response.data.user.username)     
        router.push('/admin/participants')
        
      } catch (error) {
        if (error.response?.status === 400) {
          if (error.response.data.username || error.response.data.password) {
            errors.value = error.response.data
          } else {
            generalError.value = error.response.data.message || 'Credenciales inválidas'
          }
        } else if (error.response?.status === 401) {
          generalError.value = 'Usuario o contraseña incorrectos'
        } else {
          generalError.value = 'Error de conexión. Por favor, intenta de nuevo.'
        }
        console.error('Admin login error:', error)
      } finally {
        loading.value = false
      }
    }

    return {
      form,
      loading,
      errors,
      generalError,
      login
    }
  }
}
</script>

<style scoped>
.admin-login-container {
  position: relative;
  min-height: 100vh;
  padding: 40px 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: #3a103a;
}

.admin-login-container::before {
  content: '';
  position: absolute;
  inset: 0;
  background: 
    linear-gradient(rgba(50, 10, 60, 0.2), rgba(20, 5, 35, 0.3)),
    url('/sanvalentin.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  filter: brightness(1.1) saturate(1.1);
  z-index: 0;
}

.login-card {
  position: relative;
  z-index: 1;
  backdrop-filter: blur(6px);
  background: rgba(255,255,255,0.95);
  border-radius: 20px;
  padding: 40px;
  max-width: 480px;
  width: 100%;
  box-shadow: 0 20px 40px rgba(0,0,0,0.2);
}

.card-header {
  text-align: center;
  margin-bottom: 2rem;
}

.card-header h1 {
  color: #2c3e50;
  font-size: 2rem;
  margin-bottom: 0.5rem;
  font-weight: 700;
}

.card-header p {
  color: #7f8c8d;
  font-size: 0.9rem;
  margin-top: -0.5rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.5rem;
  font-size: 0.95rem;
}

.form-group input {
  padding: 14px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
  background: #fafafa;
}

.form-group input:focus {
  outline: none;
  border-color: #3498db;
  background: white;
}

.form-group input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
  opacity: 0.7;
}

.login-button {
  background: #3498db;
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 0.5rem;
}

.login-button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 8px 25px rgba(52, 152, 219, 0.4);
}

.login-button:disabled {
  background: #95a5a6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.error {
  color: #e74c3c;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.error-message {
  background: #fdf2f2;
  border: 1px solid #fecaca;
  border-radius: 10px;
  padding: 1rem;
  text-align: center;
  margin-bottom: 1.5rem;
}

.error-icon {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}

.error-message p {
  color: #dc2626;
  margin: 0;
  font-weight: 500;
}

.back-link {
  text-align: center;
  border-top: 1px solid #e9ecef;
}

.back-text {
  color: #6c757d;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s ease;
}

.back-text:hover {
  color: #3498db;
}

@media (max-width: 768px) {
  .login-card {
    padding: 30px 20px;
    margin: 0 10px;
  }
  
  .card-header h1 {
    font-size: 1.5rem;
  }
  
  .admin-icon {
    font-size: 2.5rem;
  }
}
</style>