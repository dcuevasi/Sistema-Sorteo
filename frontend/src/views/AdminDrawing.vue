<template>
  <div class="admin-drawing-container">
    <div class="admin-header">
      <div class="header-content">
        <h1>🎲 Sorteo de San Valentín</h1>
        <div class="admin-info">
          <span class="welcome">Bienvenido, {{ adminUser }}</span>
          <router-link to="/admin/participants" class="back-button">
            ← Volver a Participantes
          </router-link>
        </div>
      </div>
    </div>

    <div class="stats-section">
      <div class="stat-card">
        <div class="stat-icon">✅</div>
        <div class="stat-info">
          <h3>{{ eligibleCount }}</h3>
          <p>Participantes Elegibles</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🏆</div>
        <div class="stat-info">
          <h3>{{ winnersCount }}</h3>
          <p>Ganadores Actuales</p>
        </div>
      </div>
    </div>

    <div class="drawing-section">
      <div v-if="!drawingStarted && winnersCount === 0" class="initial-state">
        <div class="drawing-icon">🎯</div>
        <h2>¿Listo para el Sorteo?</h2>
        <p class="drawing-description">
          Este sorteo seleccionará aleatoriamente a los ganadores entre todos los participantes verificados.
          Una vez realizado el sorteo, no se puede deshacer.
        </p>
        
        <div class="eligibility-info">
          <h3>Criterios de Elegibilidad:</h3>
          <ul>
            <li>✅ Email verificado</li>
            <li>✅ Contraseña creada</li>
            <li>✅ Registro completado</li>
          </ul>
        </div>

        <div class="drawing-controls">
          <div class="winner-count-selector">
            <label for="winnerCount">Número de ganadores:</label>
            <select id="winnerCount" v-model="selectedWinnerCount">
              <option value="1">1 ganador</option>
              <option value="2">2 ganadores</option>
              <option value="3">3 ganadores</option>
              <option value="5">5 ganadores</option>
            </select>
          </div>

          <button 
            @click="startDrawing" 
            class="start-drawing-button"
            :disabled="eligibleCount === 0"
          >
            Iniciar Sorteo
          </button>
        </div>

        <div v-if="eligibleCount === 0" class="no-participants-warning">
          ⚠️ No hay participantes elegibles para el sorteo
        </div>
      </div>

      <div v-else-if="drawingStarted && !drawingComplete" class="drawing-animation">
        <div class="roulette-container">
          <div class="roulette" :class="{ spinning: isSpinning }">
            <div class="roulette-center"></div>
          </div>
        </div>
        <h2>🎲 Realizando Sorteo...</h2>
        <p>Seleccionando {{ selectedWinnerCount }} ganador(es) de {{ eligibleCount }} participantes</p>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: progress + '%' }"></div>
        </div>
      </div>

      <div v-else-if="drawingComplete || winnersCount > 0" class="results-section">
        <div class="results-header">
          <div class="celebration-icon">🎉</div>
          <h2>¡Sorteo Completado!</h2>
          <p v-if="newWinners.length > 0">
            Se han seleccionado {{ newWinners.length }} nuevo(s) ganador(es)
          </p>
          <p v-else>
            Mostrando ganadores actuales del sorteo
          </p>
        </div>

        <div class="winners-list">
          <div 
            v-for="(winner, index) in currentWinners" 
            :key="winner.id"
            class="winner-card"
            :class="{ 'new-winner': newWinners.includes(winner) }"
          >
            <div class="winner-position">
              <span class="position-number">{{ index + 1 }}</span>
              <span class="trophy">🏆</span>
            </div>
            <div class="winner-info">
              <h3>{{ winner.full_name }}</h3>
              <p class="winner-email">{{ winner.email }}</p>
              <p class="winner-phone">{{ winner.phone }}</p>
              <div class="winner-date">
                Ganador desde: {{ formatDate(winner.winner_selected_at) }}
              </div>
            </div>
            <div v-if="newWinners.includes(winner)" class="new-badge">
              ¡NUEVO!
            </div>
          </div>
        </div>

        <div class="post-drawing-actions">
          <button 
            v-if="newWinners.length > 0"
            @click="notifyWinners" 
            class="notify-button"
            :disabled="notifying"
          >
            {{ notifying ? '📧 Enviando...' : '📧 Notificar Ganadores' }}
          </button>
          
          <button 
            v-if="eligibleCount > currentWinners.length"
            @click="selectMoreWinners" 
            class="more-winners-button"
          >
            🎲 Seleccionar Más Ganadores
          </button>
          
          <button 
            @click="notifyWinners" 
            class="export-button"
            :disabled="notifying || winnersCount === 0"
          >
            {{ notifying ? '� Enviando...' : 'Enviar mail a ganadores' }}
          </button>
        </div>

        <div v-if="notificationSent" class="notification-success">
          <div class="success-icon">✅</div>
          <p>¡Notificaciones enviadas exitosamente a todos los ganadores!</p>
        </div>
      </div>

      <div v-if="error" class="error-message">
        <div class="error-icon">❌</div>
        <h3>Error en el Sorteo</h3>
        <p>{{ error }}</p>
        <button @click="resetDrawing" class="retry-button">
          🔄 Reintentar
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { contestAPI } from '../services/api.js'

export default {
  name: 'AdminDrawing',
  setup() {
    const router = useRouter()
    
    const adminUser = ref(localStorage.getItem('adminUser') || 'Admin')
    const participants = ref([])
    const winners = ref([])
    const newWinners = ref([])
    const selectedWinnerCount = ref(1)
    const drawingStarted = ref(false)
    const drawingComplete = ref(false)
    const isSpinning = ref(false)
    const progress = ref(0)
    const notifying = ref(false)
    const notificationSent = ref(false)
    const error = ref('')

    const eligibleCount = computed(() => {
      return participants.value.filter(p => 
        p.verification_status === 'verified' && !p.is_winner
      ).length
    })

    const winnersCount = computed(() => {
      return winners.value.length
    })

    const currentWinners = computed(() => {
      return winners.value
    })

    const loadData = async () => {
      try {
        const [participantsResponse, winnersResponse] = await Promise.all([
          contestAPI.getParticipants(),
          contestAPI.getWinners()
        ])
        
        participants.value = participantsResponse.data.participants
        winners.value = winnersResponse.data.winners
        
      } catch (err) {
        if (err.response?.status === 401) {
          router.push('/admin/login')
        } else {
          error.value = 'Error al cargar los datos'
        }
        console.error('Load data error:', err)
      }
    }

    const startDrawing = async () => {
      drawingStarted.value = true
      isSpinning.value = true
      error.value = ''
      progress.value = 0

      const progressInterval = setInterval(() => {
        if (progress.value < 90) {
          progress.value += Math.random() * 10
        }
      }, 200)

      try {
        await new Promise(resolve => setTimeout(resolve, 3000))
        
        const response = await contestAPI.selectWinner(selectedWinnerCount.value)
        
        clearInterval(progressInterval)
        progress.value = 100
        
        newWinners.value = response.data.winners
        winners.value = [...winners.value, ...newWinners.value]
        
        participants.value = participants.value.map(p => {
          const isNewWinner = newWinners.value.find(w => w.id === p.id)
          if (isNewWinner) {
            return { ...p, is_winner: true }
          }
          return p
        })
        
        setTimeout(() => {
          isSpinning.value = false
          drawingComplete.value = true
        }, 1000)
        
      } catch (err) {
        clearInterval(progressInterval)
        isSpinning.value = false
        drawingStarted.value = false
        
        if (err.response?.status === 400) {
          error.value = err.response.data.message || 'Error al realizar el sorteo'
        } else {
          error.value = 'Error de conexión durante el sorteo'
        }
        console.error('Drawing error:', err)
      }
    }

    const selectMoreWinners = () => {
      drawingStarted.value = false
      drawingComplete.value = false
      newWinners.value = []
    }

    const notifyWinners = async () => {
      notifying.value = true
      
      try {
        await contestAPI.notifyWinners()
        notificationSent.value = true
        
        setTimeout(() => {
          notificationSent.value = false
        }, 5000)
        
      } catch (err) {
        error.value = 'Error al enviar las notificaciones'
        console.error('Notify winners error:', err)
      } finally {
        notifying.value = false
      }
    }

    const resetDrawing = () => {
      drawingStarted.value = false
      drawingComplete.value = false
      isSpinning.value = false
      progress.value = 0
      error.value = ''
      newWinners.value = []
      loadData()
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString('es-CL', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    onMounted(() => {
      loadData()
    })

    return {
      adminUser,
      eligibleCount,
      winnersCount,
      currentWinners,
      selectedWinnerCount,
      drawingStarted,
      drawingComplete,
      isSpinning,
      progress,
      notifying,
      notificationSent,
      error,
      newWinners,
      startDrawing,
      selectMoreWinners,
      notifyWinners,
      resetDrawing,
      formatDate
    }
  }
}
</script>

<style scoped>
.admin-drawing-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.admin-header {
  background: white;
  border-radius: 15px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h1 {
  color: #2c3e50;
  margin: 0;
  font-size: 2rem;
}

.admin-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.welcome {
  color: #7f8c8d;
  font-weight: 500;
}

.back-button {
  background: #95a5a6;
  color: white;
  padding: 8px 16px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 500;
  transition: background 0.3s ease;
}

.back-button:hover {
  background: #7f8c8d;
}

.stats-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border-radius: 15px;
  padding: 2rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

.stat-icon {
  font-size: 3rem;
}

.stat-info h3 {
  font-size: 2.5rem;
  margin: 0;
  color: #2c3e50;
  font-weight: 700;
}

.stat-info p {
  margin: 0;
  color: #7f8c8d;
  font-weight: 500;
}

.drawing-section {
  background: white;
  border-radius: 20px;
  padding: 3rem;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
  text-align: center;
}

/* Estado inicial */
.initial-state .drawing-icon {
  font-size: 4rem;
  margin-bottom: 1.5rem;
}

.initial-state h2 {
  color: #2c3e50;
  margin-bottom: 1rem;
  font-size: 2rem;
}

.drawing-description {
  color: #7f8c8d;
  font-size: 1.1rem;
  line-height: 1.6;
  margin-bottom: 1rem;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.eligibility-info {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 15px;
  margin: 1rem 0;
  text-align: left;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

.eligibility-info h3 {
  color: #2c3e50;
  margin-bottom: 1rem;
  text-align: center;
}

.eligibility-info ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.eligibility-info li {
  padding: 0.5rem 0;
  color: #27ae60;
  font-weight: 500;
}

.drawing-controls {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
  margin: 0.5rem 0;
}

.winner-count-selector {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.winner-count-selector label {
  font-weight: 600;
  color: #2c3e50;
}

.winner-count-selector select {
  padding: 10px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  background: white;
}

.start-drawing-button {
  background: linear-gradient(45deg, #e74c3c, #c0392b);
  color: white;
  border: none;
  padding: 16px 32px;
  border-radius: 12px;
  font-size: 1.2rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.start-drawing-button:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 10px 25px rgba(231, 76, 60, 0.4);
}

.start-drawing-button:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.no-participants-warning {
  background: #fff3cd;
  color: #856404;
  padding: 1rem;
  border-radius: 8px;
  margin-top: 1rem;
  font-weight: 500;
}

.drawing-animation h2 {
  color: #2c3e50;
  margin: 2rem 0 1rem;
  font-size: 2rem;
}

.drawing-animation p {
  color: #7f8c8d;
  font-size: 1.1rem;
  margin-bottom: 2rem;
}

.roulette-container {
  display: flex;
  justify-content: center;
  margin-bottom: 2rem;
}

.roulette {
  width: 150px;
  height: 150px;
  border: 8px solid #3498db;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  background: linear-gradient(45deg, #3498db, #2980b9);
}

.roulette.spinning {
  animation: spin 2s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.roulette-center {
  font-size: 3rem;
  color: white;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
  margin: 1rem 0;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3498db, #2980b9);
  border-radius: 4px;
  transition: width 0.3s ease;
}

/* Resultados */
.results-header {
  margin-bottom: 2rem;
}

.celebration-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.results-header h2 {
  color: #27ae60;
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.results-header p {
  color: #7f8c8d;
  font-size: 1.1rem;
}

.winners-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin: 2rem 0;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}

.winner-card {
  display: flex;
  align-items: center;
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 15px;
  position: relative;
}

.winner-card.new-winner {
  background: linear-gradient(135deg, #fff3e0, #ffe0b2);
  border: 2px solid #ff9800;
}

.winner-position {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-right: 1.5rem;
}

.position-number {
  background: #3498db;
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 1.2rem;
}

.trophy {
  font-size: 2rem;
  margin-top: 0.5rem;
}

.winner-info {
  flex: 1;
  text-align: left;
}

.winner-info h3 {
  color: #2c3e50;
  margin: 0 0 0.5rem;
  font-size: 1.3rem;
}

.winner-email,
.winner-phone {
  color: #7f8c8d;
  margin: 0.25rem 0;
  font-size: 0.95rem;
}

.winner-date {
  color: #27ae60;
  font-size: 0.85rem;
  font-weight: 500;
  margin-top: 0.5rem;
}

.new-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background: #ff9800;
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: bold;
}

.post-drawing-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
  margin: 2rem 0;
}

.notify-button,
.more-winners-button,
.export-button {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.notify-button {
  background: #27ae60;
  color: white;
}

.notify-button:hover:not(:disabled) {
  background: #229954;
  transform: translateY(-2px);
}

.notify-button:disabled {
  background: #95a5a6;
  cursor: not-allowed;
}

.more-winners-button {
  background: #f39c12;
  color: white;
}

.more-winners-button:hover {
  background: #e67e22;
  transform: translateY(-2px);
}

.export-button {
  background: #8e44ad;
  color: white;
}

.export-button:hover {
  background: #7d3c98;
  transform: translateY(-2px);
}

.notification-success {
  background: #d4edda;
  border: 1px solid #c3e6cb;
  border-radius: 10px;
  padding: 1rem;
  margin-top: 1rem;
}

.success-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.notification-success p {
  color: #155724;
  margin: 0;
  font-weight: 500;
}

.error-message {
  background: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 10px;
  padding: 2rem;
  margin: 2rem 0;
}

.error-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.error-message h3 {
  color: #721c24;
  margin-bottom: 1rem;
}

.error-message p {
  color: #721c24;
  margin-bottom: 1.5rem;
}

.retry-button {
  background: #dc3545;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
}

.retry-button:hover {
  background: #c82333;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .drawing-section {
    padding: 1.5rem;
  }
  
  .drawing-controls {
    align-items: stretch;
  }
  
  .winner-count-selector {
    flex-direction: column;
    text-align: center;
  }
  
  .winner-card {
    flex-direction: column;
    text-align: center;
    gap: 1rem;
  }
  
  .winner-position {
    margin-right: 0;
  }
  
  .post-drawing-actions {
    flex-direction: column;
  }
}
</style>