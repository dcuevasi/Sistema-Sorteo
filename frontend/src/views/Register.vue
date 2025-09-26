<template>
  <div class="register-container">
    <div class="register-card">
      <div class="card-header">
        <h1>Regístrate</h1>
        <p>Completa tus datos para participar</p>
      </div>

      <form @submit.prevent="submitRegistration" class="register-form">
        <div class="form-group">
          <label for="fullName">Nombre Completo *</label>
          <input
            id="fullName"
            v-model="form.full_name"
            type="text"
            required
            placeholder="Ej: María González"
            :disabled="loading"
          />
          <span v-if="errors.full_name" class="error">{{ errors.full_name[0] }}</span>
        </div>

        <div class="form-group">
          <label for="email">Correo Electrónico *</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            required
            placeholder="maria@ejemplo.com"
            :disabled="loading"
          />
          <span v-if="errors.email" class="error">{{ errors.email[0] }}</span>
        </div>

        <div class="form-group">
          <label for="phone">Teléfono *</label>
          <input
            id="phone"
            v-model="form.phone"
            type="tel"
            required
            placeholder="+56912345678"
            :disabled="loading"
          />
          <span v-if="errors.phone" class="error">{{ errors.phone[0] }}</span>
        </div>

        <div class="form-group">
          <label class="checkbox-label">
            <input
              v-model="acceptTerms"
              type="checkbox"
              required
              :disabled="loading"
            />
            Acepto los términos y condiciones del sorteo
          </label>
        </div>

        <button 
          type="submit" 
          class="submit-button"
          :disabled="loading || !acceptTerms"
        >
          {{ loading ? 'Registrando...' : 'Registrarse' }}
        </button>
      </form>

      <div v-if="generalError" class="error-message">
        <div class="error-icon">❌</div>
        <p>{{ generalError }}</p>
        <button @click="resetForm" class="retry-button">
          Intentar de Nuevo
        </button>
      </div>
    </div>

    <div v-if="success" class="modal-overlay" @click="closeModal">
      <div class="success-modal" @click.stop>
        <div class="success-icon">✅</div>
        <h2>¡Registro Exitoso!</h2>
        <p>{{ successMessage }}</p>
        <div class="next-steps">
          <h3>Próximos pasos:</h3>
          <ol>
            <li>Revisa tu correo electrónico</li>
            <li>Haz clic en el enlace de verificación</li>
            <li>Crea tu contraseña</li>
            <li>¡Ya estarás participando!</li>
          </ol>
        </div>
        <div class="modal-actions">
          <router-link to="/" class="back-button">
            Volver al Inicio
          </router-link>
          <button @click="closeModal" class="close-modal-button">
            Cerrar
          </button>
        </div>
      </div>
    </div>

    <div class="back-link">
      <router-link to="/" class="back-text">
        ← Volver al inicio
      </router-link>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { contestAPI } from '../services/api.js'

export default {
  name: 'Register',
  setup() {
    const form = reactive({
      full_name: '',
      email: '',
      phone: ''
    })
    
    const acceptTerms = ref(false)
    const loading = ref(false)
    const success = ref(false)
    const successMessage = ref('')
    const errors = ref({})
    const generalError = ref('')

    const resetForm = () => {
      form.full_name = ''
      form.email = ''
      form.phone = ''
      acceptTerms.value = false
      errors.value = {}
      generalError.value = ''
      success.value = false
    }

    const closeModal = () => {
      success.value = false
    }

    const submitRegistration = async () => {
      if (!acceptTerms.value) {
        generalError.value = 'Debes aceptar los términos y condiciones'
        return
      }

      loading.value = true
      errors.value = {}
      generalError.value = ''

      try {
        const response = await contestAPI.registerParticipant(form)
        
        success.value = true
        successMessage.value = response.data.message
        
        // Limpiar formulario
        form.full_name = ''
        form.email = ''
        form.phone = ''
        acceptTerms.value = false
        
      } catch (error) {
        if (error.response?.status === 400) {
          // Errores de validación
          if (error.response.data.email) {
            errors.value = error.response.data
          } else {
            generalError.value = error.response.data.message || 'Error en los datos enviados'
          }
        } else {
          generalError.value = 'Error de conexión. Por favor, intenta de nuevo.'
        }
        console.error('Registration error:', error)
      } finally {
        loading.value = false
      }
    }

    return {
      form,
      acceptTerms,
      loading,
      success,
      successMessage,
      errors,
      generalError,
      submitRegistration,
      resetForm,
      closeModal
    }
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.register-card {
  background: white;
  border-radius: 20px;
  padding: 40px;
  max-width: 500px;
  width: 100%;
  box-shadow: 0 20px 40px rgba(0,0,0,0.1);
}

.card-header {
  text-align: center;
  margin-bottom: 2rem;
}

.card-header h1 {
  color: #333;
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.card-header p {
  color: #666;
  font-size: 1rem;
}

.register-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-weight: 600;
  color: #333;
  margin-bottom: 0.5rem;
}

.form-group input {
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
}

.form-group input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #666;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  width: auto;
}

.submit-button {
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

.submit-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

.submit-button:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.error {
  color: #dc3545;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.success-message {
  text-align: center;
  padding: 2rem 0;
}

.success-icon {
  font-size: 2rem;
  margin-bottom: 1rem;
}

.success-message h2 {
  color: #28a745;
  margin-bottom: 1rem;
}

.success-message p {
  color: #666;
  margin-bottom: 1.5rem;
}

.next-steps {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 10px;
  text-align: left;
}

.next-steps h3 {
  color: #333;
}

.next-steps ol {
  color: #666;
  padding-left: 1.5rem;
}

.next-steps li {
}

.back-button {
  display: inline-block;
  background: linear-gradient(45deg, #667eea, #764ba2);
  color: white;
  padding: 12px 24px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  transition: transform 0.3s ease;
}

.back-button:hover {
  transform: translateY(-2px);
}

.error-message {
  text-align: center;
  padding: 2rem 0;
  color: #dc3545;
}

.error-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.retry-button {
  background: #dc3545;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  margin-top: 1rem;
}

.retry-button:hover {
  background: #c82333;
}

.back-link {
  margin-top: 2rem;
}

.back-text {
  color: rgba(255,255,255,0.8);
  text-decoration: none;
  font-weight: 500;
}

.back-text:hover {
  color: white;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.success-modal {
  background: white;
  border-radius: 20px;
  padding: 30px 40px;
  max-width: 500px;
  width: 100%;
  max-height: 80vh;
  overflow-y: auto;
  text-align: center;
  box-shadow: 0 20px 40px rgba(0,0,0,0.3);
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-50px) scale(0.9);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.success-modal .success-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.success-modal h2 {
  color: #27ae60;
  font-size: 1.5rem;
  margin-bottom: 1rem;
  font-weight: 700;
}

.success-modal p {
  color: #7f8c8d;
  font-size: 1rem;
  line-height: 1;
}

.next-steps {
  background: #f8f9fa;
  border-radius: 12px;
  margin-bottom: 0.5rem;
  text-align: left;
}

.next-steps h3 {
  color: #2c3e50;
  font-size: 1.2rem;
  margin-bottom: 1rem;
  text-align: center;
}

.next-steps ol {
  color: #34495e;
  font-size: 1rem;
  line-height: 1.8;
  padding-left: 1.5rem;
}

.next-steps li {
  margin-bottom: 0.5rem;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.back-button,
.close-modal-button {
  padding: 8px 16px;
  border-radius: 10px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.3s ease;
  cursor: pointer;
  border: none;
  font-size: 1rem;
}

.back-button {
  background: linear-gradient(45deg, #3498db, #2980b9);
  color: white;
}

.back-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(52, 152, 219, 0.4);
}

.close-modal-button {
  background: #95a5a6;
  color: white;
}

.close-modal-button:hover {
  background: #7f8c8d;
  transform: translateY(-2px);
}

@media (max-width: 768px) {
  .register-card {
    padding: 30px 20px;
    margin: 0 10px;
  }
  
  .card-header h1 {
    font-size: 1.5rem;
  }

  .success-modal {
    padding: 30px 20px;
    margin: 0 10px;
  }

  .success-modal h2 {
    font-size: 1.5rem;
  }

  .success-modal .success-icon {
    font-size: 1rem;
  }

  .modal-actions {
    flex-direction: column;
  }

  .back-button,
  .close-modal-button {
    width: 100%;
    text-align: center;
  }
}
</style>