<template>
  <div class="verification-container">
    <div class="verification-card">
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <h2>Verificando tu email...</h2>
        <p>Por favor espera mientras procesamos tu verificación</p>
      </div>

      <div v-else-if="success" class="success-state">
        <div class="success-icon">✅</div>
        <h1>¡Email Verificado!</h1>
        <p class="success-subtitle">{{ successMessage }}</p>
        
        <form @submit.prevent="createPassword" class="password-form">
          <h3>Crea tu contraseña</h3>
          <p class="form-subtitle">Para completar tu registro, crea una contraseña segura</p>
          
          <div class="form-group">
            <label for="password">Nueva Contraseña *</label>
            <input
              id="password"
              v-model="passwordForm.password"
              type="password"
              required
              placeholder="Mínimo 8 caracteres"
              :disabled="creatingPassword"
            />
            <span v-if="passwordErrors.password" class="error">{{ passwordErrors.password[0] }}</span>
          </div>

          <div class="form-group">
            <label for="confirmPassword">Confirmar Contraseña *</label>
            <input
              id="confirmPassword"
              v-model="passwordForm.password_confirm"
              type="password"
              required
              placeholder="Repite tu contraseña"
              :disabled="creatingPassword"
            />
            <span v-if="passwordErrors.password_confirm" class="error">{{ passwordErrors.password_confirm[0] }}</span>
          </div>

          <button 
            type="submit" 
            class="create-password-button"
            :disabled="creatingPassword"
          >
            {{ creatingPassword ? 'Creando...' : 'Crear Contraseña' }}
          </button>
        </form>

        <div v-if="passwordCreated" class="password-success">
          <div class="success-icon">🎉</div>
          <h3>¡Registro Completado!</h3>
          <p>Tu contraseña ha sido creada exitosamente. Ya estás participando en el sorteo.</p>
          <router-link to="/" class="home-button">
            Ir al Inicio
          </router-link>
        </div>
      </div>

      <div v-else-if="error" class="error-state">
        <div class="error-icon">❌</div>
        <h1>Error de Verificación</h1>
        <p class="error-message">{{ errorMessage }}</p>
        
        <div class="error-actions">
          <button @click="retryVerification" class="retry-button">
            Intentar de Nuevo
          </button>
          <router-link to="/register" class="register-again-button">
            Registrarse de Nuevo
          </router-link>
        </div>
      </div>

      <div v-else class="initial-state">
        <div class="mail-icon">📧</div>
        <h1>Verificación de Email</h1>
        <p>Para verificar tu email, necesitas hacer clic en el enlace que te enviamos por correo.</p>
        
        <div class="instructions">
          <h3>¿No encuentras el email?</h3>
          <ul>
            <li>Revisa tu carpeta de spam o correo no deseado</li>
            <li>Asegúrate de que ingresaste el email correcto</li>
            <li>El enlace de verificación expira en 24 horas</li>
          </ul>
        </div>

        <div class="actions">
          <router-link to="/register" class="register-button">
            Registrarse de Nuevo
          </router-link>
          <router-link to="/" class="home-link">
            Volver al Inicio
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { contestAPI } from '../services/api.js'

export default {
  name: 'EmailVerification',
  setup() {
    const route = useRoute()
    const router = useRouter()
    
    const loading = ref(false)
    const success = ref(false)
    const error = ref(false)
    const successMessage = ref('')
    const errorMessage = ref('')
    
    const passwordForm = reactive({
      password: '',
      password_confirm: ''
    })
    
    const creatingPassword = ref(false)
    const passwordCreated = ref(false)
    const passwordErrors = ref({})

    const verifyEmail = async (token) => {
      loading.value = true
      error.value = false
      success.value = false

      try {
        const response = await contestAPI.verifyEmail(token)
        success.value = true
        successMessage.value = response.data.message
      } catch (err) {
        error.value = true
        if (err.response?.status === 400) {
          errorMessage.value = err.response.data.message || 'Token de verificación inválido o expirado'
        } else {
          errorMessage.value = 'Error de conexión. Por favor, intenta de nuevo.'
        }
        console.error('Email verification error:', err)
      } finally {
        loading.value = false
      }
    }

    const createPassword = async () => {
      if (passwordForm.password !== passwordForm.password_confirm) {
        passwordErrors.value = {
          password_confirm: ['Las contraseñas no coinciden']
        }
        return
      }

      creatingPassword.value = true
      passwordErrors.value = {}

      try {
        const token = route.query.token
        await contestAPI.createPassword({
          token: token,
          password: passwordForm.password,
          password_confirm: passwordForm.password_confirm
        })
        
        passwordCreated.value = true
        
      } catch (err) {
        if (err.response?.status === 400) {
          passwordErrors.value = err.response.data
        } else {
          passwordErrors.value = {
            password: ['Error al crear la contraseña. Intenta de nuevo.']
          }
        }
        console.error('Password creation error:', err)
      } finally {
        creatingPassword.value = false
      }
    }

    const retryVerification = () => {
      const token = route.query.token
      if (token) {
        verifyEmail(token)
      }
    }

    onMounted(() => {
      const token = route.query.token
      if (token) {
        verifyEmail(token)
      }
    })

    return {
      loading,
      success,
      error,
      successMessage,
      errorMessage,
      passwordForm,
      creatingPassword,
      passwordCreated,
      passwordErrors,
      createPassword,
      retryVerification
    }
  }
}
</script>

<style scoped>
.verification-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.verification-card {
  background: white;
  border-radius: 20px;
  padding: 40px;
  max-width: 500px;
  width: 100%;
  box-shadow: 0 20px 40px rgba(0,0,0,0.1);
  text-align: center;
}

/* Estados de carga */
.loading-state .spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 2rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Estados de éxito */
.success-icon,
.error-icon,
.mail-icon {
  font-size: 3rem;
  margin-bottom: 0.8rem;
}

.success-state h1,
.error-state h1,
.initial-state h1,
.loading-state h2 {
  color: #333;
  margin-bottom: 0.8rem;
}

.success-subtitle,
.error-message {
  color: #666;
  margin-bottom: 0.5rem;
  line-height: 1;
}

.password-form {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 15px;
  margin: 1rem 0;
  text-align: left;
}

.password-form h3 {
  color: #333;
  margin-bottom: 0.5rem;
}

.form-subtitle {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  font-weight: 600;
  color: #333;
  margin-bottom: 0.5rem;
}

.form-group input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
}

.form-group input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.error {
  color: #dc3545;
  font-size: 0.875rem;
  margin-top: 0.25rem;
  display: block;
}

.create-password-button {
  width: 100%;
  background: linear-gradient(45deg, #667eea, #764ba2);
  color: white;
  border: none;
  padding: 15px 30px;
  border-radius: 10px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.create-password-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

.create-password-button:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* Mensaje de contraseña creada */
.password-success {
  background: #d4edda;
  padding: 2rem;
  border-radius: 15px;
  margin-top: 2rem;
}

.password-success h3 {
  color: #155724;
  margin-bottom: 1rem;
}

.password-success p {
  color: #155724;
  margin-bottom: 1.5rem;
}

/* Botones y enlaces */
.home-button,
.register-button,
.retry-button,
.register-again-button {
  display: inline-block;
  padding: 12px 24px;
  border-radius: 10px;
  text-decoration: none;
  font-weight: 600;
  text-align: center;
  transition: all 0.3s ease;
  margin: 0.5rem;
}

.home-button,
.register-button {
  background: linear-gradient(45deg, #667eea, #764ba2);
  color: white;
}

.home-button:hover,
.register-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

.retry-button {
  background: #28a745;
  color: white;
  border: none;
  cursor: pointer;
}

.retry-button:hover {
  background: #218838;
  transform: translateY(-2px);
}

.register-again-button {
  background: #6c757d;
  color: white;
}

.register-again-button:hover {
  background: #5a6268;
  transform: translateY(-2px);
}

.home-link {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
  margin-top: 1rem;
  display: inline-block;
}

.home-link:hover {
  text-decoration: underline;
}

.instructions {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 10px;
  margin: 2rem 0;
  text-align: left;
}

.instructions h3 {
  color: #333;
  margin-bottom: 1rem;
}

.instructions ul {
  color: #666;
  padding-left: 1.5rem;
}

.instructions li {
  margin-bottom: 0.5rem;
}

.error-actions {
  margin-top: 2rem;
}

@media (max-width: 768px) {
  .verification-card {
    padding: 30px 20px;
    margin: 0 10px;
  }
  
  .password-form {
    padding: 1.5rem;
  }
  
  .home-button,
  .register-button,
  .retry-button,
  .register-again-button {
    display: block;
    width: 100%;
    margin: 0.5rem 0;
  }
}
</style>