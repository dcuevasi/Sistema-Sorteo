<template>
  <div class="admin-participants-container">
    <div class="admin-header">
      <div class="header-content">
        <h1>Panel de administración</h1>
        <div class="admin-info">
          <span class="welcome">Bienvenido, {{ adminUser }}</span>
          <button @click="logout" class="logout-button">Cerrar Sesión</button>
        </div>
      </div>
    </div>

    <div class="stats-section">
      <div class="stat-card">
        <div class="stat-icon">👥</div>
        <div class="stat-info">
          <h3>{{ stats.totalParticipants }}</h3>
          <p>Total Participantes</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">✅</div>
        <div class="stat-info">
          <h3>{{ stats.verifiedParticipants }}</h3>
          <p>Verificados</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">⏳</div>
        <div class="stat-info">
          <h3>{{ stats.pendingParticipants }}</h3>
          <p>Pendientes</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🏆</div>
        <div class="stat-info">
          <h3>{{ stats.winners }}</h3>
          <p>Ganadores</p>
        </div>
      </div>
    </div>

    <div class="controls-section">
      <div class="search-box">
        <input
          v-model="searchTerm"
          type="text"
          placeholder="Buscar por nombre o email..."
          class="search-input"
        />
        <div class="search-icon">🔍</div>
      </div>
      
      <div class="filter-controls">
        <select v-model="statusFilter" class="status-filter">
          <option value="">Todos los estados</option>
          <option value="pending">Pendientes</option>
          <option value="verified">Verificados</option>
          <option value="winner">Ganadores</option>
        </select>
        
        <button @click="refreshData" class="refresh-button" :disabled="loading">
          {{ loading ? '⏳' : '🔄' }}
        </button>
        
        <router-link to="/admin/drawing" class="drawing-button">
          🎲 Realizar Sorteo
        </router-link>
      </div>
    </div>

    <div class="participants-section">
      <div v-if="loading" class="loading-message">
        <div class="spinner"></div>
        <p>Cargando participantes...</p>
      </div>

      <div v-else-if="error" class="error-message">
        <div class="error-icon">❌</div>
        <p>{{ error }}</p>
        <button @click="refreshData" class="retry-button">Reintentar</button>
      </div>

      <div v-else-if="filteredParticipants.length === 0" class="empty-message">
        <div class="empty-icon">📭</div>
        <h3>No se encontraron participantes</h3>
        <p v-if="searchTerm || statusFilter">
          Intenta ajustar los filtros de búsqueda
        </p>
        <p v-else>
          Aún no hay participantes registrados
        </p>
      </div>

      <div v-else class="participants-table">
        <div class="table-header">
          <div class="header-cell">Participante</div>
          <div class="header-cell">Email</div>
          <div class="header-cell">Teléfono</div>
          <div class="header-cell">Estado</div>
          <div class="header-cell">Fecha Registro</div>
          <div class="header-cell">Acciones</div>
        </div>

        <div 
          v-for="participant in paginatedParticipants" 
          :key="participant.id"
          class="table-row"
        >
          <div class="cell participant-info">
            <div class="participant-name">{{ participant.full_name }}</div>
            <div v-if="participant.is_winner" class="winner-badge">🏆 GANADOR</div>
          </div>
          
          <div class="cell email" :title="participant.email">{{ participant.email }}</div>
          
          <div class="cell">{{ participant.phone }}</div>
          
          <div class="cell">
            <span 
              :class="['status-badge', getStatusClass(participant)]"
            >
              {{ getStatusText(participant) }}
            </span>
          </div>
          
          <div class="cell">{{ formatDate(participant.created_at) }}</div>
          
          <div class="cell actions">
            <button 
              v-if="participant.verification_status === 'pending'"
              @click="resendVerification(participant)"
              class="action-button resend"
              title="Reenviar verificación"
            >
              Reenviar
            </button>
            <button 
              @click="viewDetails(participant)"
              class="action-button view"
              title="Ver detalles"
            >
              Detalles
            </button>
          </div>
        </div>
      </div>

      <div v-if="totalPages > 1" class="pagination">
        <button 
          @click="currentPage = Math.max(1, currentPage - 1)"
          :disabled="currentPage === 1"
          class="page-button"
        >
          ← Anterior
        </button>
        
        <span class="page-info">
          Página {{ currentPage }} de {{ totalPages }}
        </span>
        
        <button 
          @click="currentPage = Math.min(totalPages, currentPage + 1)"
          :disabled="currentPage === totalPages"
          class="page-button"
        >
          Siguiente →
        </button>
      </div>
    </div>

    <div v-if="selectedParticipant" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Detalles del Participante</h3>
          <button @click="closeModal" class="close-button">×</button>
        </div>
        <div class="modal-body">
          <div class="detail-group">
            <label>Nombre Completo:</label>
            <span>{{ selectedParticipant.full_name }}</span>
          </div>
          <div class="detail-group">
            <label>Email:</label>
            <span>{{ selectedParticipant.email }}</span>
          </div>
          <div class="detail-group">
            <label>Teléfono:</label>
            <span>{{ selectedParticipant.phone }}</span>
          </div>
          <div class="detail-group">
            <label>Estado:</label>
            <span :class="['status-badge', getStatusClass(selectedParticipant)]">
              {{ getStatusText(selectedParticipant) }}
            </span>
          </div>
          <div class="detail-group">
            <label>Fecha de Registro:</label>
            <span>{{ formatDate(selectedParticipant.created_at) }}</span>
          </div>
          <div v-if="selectedParticipant.verified_at" class="detail-group">
            <label>Fecha de Verificación:</label>
            <span>{{ formatDate(selectedParticipant.verified_at) }}</span>
          </div>
          <div v-if="selectedParticipant.is_winner" class="detail-group winner-info">
            <label>🏆 ¡Es Ganador!</label>
            <span>Este participante ha sido seleccionado como ganador</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { contestAPI } from '../services/api.js'

export default {
  name: 'AdminParticipants',
  setup() {
    const router = useRouter()
    
    const adminUser = ref(localStorage.getItem('adminUser') || 'Admin')
    const participants = ref([])
    const winners = ref([])
    const loading = ref(false)
    const error = ref('')
    const searchTerm = ref('')
    const statusFilter = ref('')
    const currentPage = ref(1)
    const pageSize = 10
    const selectedParticipant = ref(null)

    const stats = computed(() => {
      const total = participants.value.length
      const verified = participants.value.filter(p => p.verification_status === 'verified').length
      const pending = participants.value.filter(p => p.verification_status === 'pending').length
      const winnersCount = winners.value.length
      return {
        totalParticipants: total,
        verifiedParticipants: verified,
        pendingParticipants: pending,
        winners: winnersCount
      }
    })

    const filteredParticipants = computed(() => {
      let filtered = participants.value
      if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase()
        filtered = filtered.filter(p => 
          p.full_name.toLowerCase().includes(term) ||
          p.email.toLowerCase().includes(term)
        )
      }

      if (statusFilter.value) {
        if (statusFilter.value === 'winner') {
          filtered = filtered.filter(p => p.is_winner)
        } else {
          filtered = filtered.filter(p => p.verification_status === statusFilter.value)
        }
      }

      return filtered
    })

    const totalPages = computed(() => {
      return Math.ceil(filteredParticipants.value.length / pageSize)
    })

    const paginatedParticipants = computed(() => {
      const start = (currentPage.value - 1) * pageSize
      const end = start + pageSize
      return filteredParticipants.value.slice(start, end)
    })

    const loadParticipants = async () => {
      loading.value = true
      error.value = ''

      try {
        const [participantsResponse, winnersResponse] = await Promise.all([
          contestAPI.getParticipants(),
          contestAPI.getWinners().catch(() => ({ data: { winners: [] }}))
        ])

        participants.value = participantsResponse.data.participants
        winners.value = winnersResponse.data.winners || []

        if (winners.value.length) {
          const winnerIds = new Set(winners.value.map(w => w.id))
          participants.value = participants.value.map(p => ({
            ...p,
            is_winner: winnerIds.has(p.id)
          }))
        }
      } catch (err) {
        if (err.response?.status === 401) {
          router.push('/admin/login')
        } else {
          error.value = 'Error al cargar los participantes'
        }
        console.error('Load participants error:', err)
      } finally {
        loading.value = false
      }
    }

    const refreshData = () => {
      loadParticipants()
    }

    const logout = () => {
      localStorage.removeItem('adminToken')
      localStorage.removeItem('adminUser')
      router.push('/admin/login')
    }

    const getStatusClass = (participant) => {
      if (participant.is_winner) return 'winner'
      return participant.verification_status
    }

    const getStatusText = (participant) => {
      if (participant.is_winner) return 'Ganador'
      return participant.verification_status === 'verified' ? 'Verificado' : 'Pendiente'
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

    const resendVerification = async (participant) => {
      try {
        await contestAPI.resendVerification(participant.email)
        alert('Email de verificación reenviado exitosamente')
      } catch (err) {
        alert('Error al reenviar el email de verificación')
        console.error('Resend verification error:', err)
      }
    }

    const viewDetails = (participant) => {
      selectedParticipant.value = participant
    }

    const closeModal = () => {
      selectedParticipant.value = null
    }

    onMounted(() => {
      loadParticipants()
    })

    return {
      adminUser,
      participants,
      winners,
      loading,
      error,
      searchTerm,
      statusFilter,
      currentPage,
      selectedParticipant,
      stats,
      filteredParticipants,
      totalPages,
      paginatedParticipants,
      refreshData,
      logout,
      getStatusClass,
      getStatusText,
      formatDate,
      resendVerification,
      viewDetails,
      closeModal
    }
  }
}
</script>

<style scoped>
.admin-participants-container {
  min-height: 100vh;
  background: #e0e0e0ff;
  padding: 20px;
}

.admin-header {
  background: white;
  border-radius: 15px;
  padding: 2rem;
  margin-bottom: 1.3rem;
  box-shadow: 0 5px 15px rgba(0,0,0,0.08);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h1 {
  color: #2c3e50;
  margin: 0;
  font-size: 1.5rem;
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

.logout-button {
  background: #e74c3c;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.3s ease;
}

.logout-button:hover {
  background: #c0392b;
}

.stats-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border-radius: 15px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 5px 15px rgba(0,0,0,0.08);
}

.stat-icon {
  font-size: 2.5rem;
}

.stat-info h3 {
  font-size: 2rem;
  margin: 0;
  color: #2c3e50;
}

.stat-info p {
  margin: 0;
  color: #7f8c8d;
  font-weight: 500;
}

.controls-section {
  background: white;
  border-radius: 15px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 5px 15px rgba(0,0,0,0.08);
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.search-box {
  position: relative;
  flex: 1;
  min-width: 250px;
}

.search-input {
  width: 100%;
  padding: 12px 40px 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  font-size: 1rem;
  box-sizing: border-box;
}

.search-input:focus {
  outline: none;
  border-color: #3498db;
}

.search-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #7f8c8d;
}

.filter-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.status-filter {
  padding: 10px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 0.9rem;
  background: white;
}

.refresh-button,
.drawing-button {
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  transition: all 0.3s ease;
}

.refresh-button {
  background: #95a5a6;
  color: white;
}

.refresh-button:hover:not(:disabled) {
  background: #7f8c8d;
}

.drawing-button {
  background: linear-gradient(45deg, #e74c3c, #c0392b);
  color: white;
}

.drawing-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(231, 76, 60, 0.4);
}

.participants-section {
  background: white;
  border-radius: 15px;
  padding: 2rem;
  box-shadow: 0 5px 15px rgba(0,0,0,0.08);
}

.loading-message,
.error-message,
.empty-message {
  text-align: center;
  padding: 3rem 1rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-icon,
.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.retry-button {
  background: #3498db;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  margin-top: 1rem;
}

.participants-table {
  width: 100%;
}

.table-header {
  display: grid;
  grid-template-columns: 2fr 2.3fr 1.4fr 1fr 1.5fr 1fr;
  gap: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 10px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.table-row {
  display: grid;
  grid-template-columns: 2fr 2.3fr 1.4fr 1fr 1.5fr 1fr;
  gap: 1rem;
  padding: 1rem;
  border-bottom: 1px solid #e9ecef;
  align-items: center;
}

.table-row:hover {
  background: #f8f9fa;
}

.participant-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.participant-name {
  font-weight: 600;
  color: #2c3e50;
}

.cell.email {
  max-width: 260px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.winner-badge {
  font-size: 0.75rem;
  color: #f39c12;
  font-weight: 700;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-badge.verified {
  background: #d4edda;
  color: #155724;
}

.status-badge.pending {
  background: #fff3cd;
  color: #856404;
}

.status-badge.winner {
  background: #f8d7da;
  color: #721c24;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.action-button {
  padding: 6px 8px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: background 0.3s ease;
}

.action-button.resend {
  background: #3498db;
  color: white;
}

.action-button.view {
  background: #95a5a6;
  color: white;
}

.action-button:hover {
  opacity: 0.8;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid #e9ecef;
}

.page-button {
  padding: 8px 16px;
  border: 1px solid #dee2e6;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.page-button:hover:not(:disabled) {
  background: #3498db;
  color: white;
  border-color: #3498db;
}

.page-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: #7f8c8d;
  font-weight: 500;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 15px;
  padding: 0;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e9ecef;
}

.modal-header h3 {
  margin: 0;
  color: #2c3e50;
}

.close-button {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #7f8c8d;
}

.modal-body {
  padding: 1.5rem;
}

.detail-group {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
  border-bottom: 1px solid #f1f3f4;
}

.detail-group:last-child {
  border-bottom: none;
}

.detail-group label {
  font-weight: 600;
  color: #2c3e50;
}

.winner-info {
  background: #fff8e1;
  padding: 1rem;
  border-radius: 8px;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.5rem;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .controls-section {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-controls {
    justify-content: space-between;
  }
  
  .table-header,
  .table-row {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }
  
  .table-header {
    display: none;
  }
  
  .table-row {
    display: flex;
    flex-direction: column;
    background: #f8f9fa;
    border-radius: 8px;
    margin-bottom: 0.5rem;
    padding: 1rem;
  }
  
  .cell::before {
    content: attr(data-label);
    font-weight: 600;
    color: #2c3e50;
    margin-right: 0.5rem;
  }
}
</style>