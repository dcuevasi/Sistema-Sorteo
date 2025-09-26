<template>
  <div class="home-container">
    <div class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">Sorteo</h1>
        <h2 class="hero-title hero-title-secondary">San Valentín 2025</h2>
        <p class="hero-subtitle">
          Gana una estadía romántica de 2 noches para ti y tu pareja
        </p>
        <div class="hero-prize">
          <h2>Premio: Estadía de 2 noches para pareja</h2>
          <p>Hotel de lujo • Todo incluido • Experiencia romántica completa</p>
        </div>
        <div v-if="stats" class="stats-section">
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-number">{{ stats.total_registered }}</div>
              <div class="stat-label">Registrados</div>
            </div>
            <div class="stat-card">
              <div class="stat-number">{{ stats.participating }}</div>
              <div class="stat-label">Participando</div>
            </div>
            <div v-if="stats.winner_selected" class="stat-card winner-card">
              <div class="stat-number">🏆</div>
              <div class="stat-label">¡Ya hay ganador!</div>
            </div>
          </div>
        </div>
        <div class="cta-section">
          <template v-if="stats?.winner_selected">
            <button class="cta-button disabled" disabled title="El sorteo ya finalizó">
              ¡Sorteo Finalizado!
            </button>
          </template>
          <template v-else>
            <router-link to="/register" class="cta-button">
              ¡Participa Ahora!
            </router-link>
          </template>
          <div class="admin-link">
            <router-link to="/admin/login" class="admin-button">
              Panel Administrador
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { contestAPI } from '../services/api.js'

export default {
  name: 'Home',
  setup() {
    const stats = ref(null)
    const loading = ref(true)
    const error = ref(null)

    const loadStats = async () => {
      try {
        loading.value = true
        const response = await contestAPI.getStats()
        stats.value = response.data
      } catch (err) {
        error.value = 'Error al cargar las estadísticas'
        console.error('Error loading stats:', err)
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      loadStats()
      setInterval(loadStats, 30000)
    })

    return {
      stats,
      loading,
      error
    }
  }
}
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.hero-section {
  padding: 40px 20px;
  text-align: center;
  color: white;
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
}

.hero-title {
  font-size: 3rem;
  font-weight: bold;
  margin-bottom: 1rem;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.hero-title-secondary {
  font-size: 2rem;
  font-weight: 600;
  margin-top: -1rem;
  display: block;
}

.hero-subtitle {
  font-size: 1.05rem;
  margin-bottom: 0.5rem;
  opacity: 0.9;
}

.hero-prize {
  background: rgba(105, 50, 124, 0.7);
  padding: 1rem;
  border-radius: 7px;
  margin: 1rem 0;
  backdrop-filter: blur(10px);
}

.hero-prize h2 {
  color: #ffeb3b;
  margin-bottom: 0.5rem;
}

.stats-section {
  margin: 1.5rem 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  max-width: 600px;
  margin: 0 auto;
}

.stat-card {
  background: rgba(255,255,255,0.2);
  padding: 1rem;
  border-radius: 5px;
  backdrop-filter: blur(10px);
}

.stat-number {
  font-size: 2.5rem;
  font-weight: bold;
  color: #ffeb3b;
}

.stat-label {
  font-size: 0.9rem;
  opacity: 0.9;
}

.winner-card {
  background: rgba(255, 215, 0, 0.3);
  border: 2px solid #ffd700;
}

.cta-section {
  margin-top: 1rem;
}

.cta-button {
  display: inline-block;
  background: linear-gradient(45deg, #ff6b6b, #ee5a52);
  color: white;
  padding: 18px 40px;
  border-radius: 10px;
  font-size: 1.3rem;
  font-weight: bold;
  text-decoration: none;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.cta-button:hover:not(.disabled) {
  transform: translateY(-1.5px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.3);
}

.cta-button.disabled {
  background: #6c757d;
  cursor: not-allowed;
  opacity: 0.7;
  pointer-events: none;
}

.admin-link {
  margin-top: 1rem;
}

.admin-button {
  color: rgba(255,255,255,0.8);
  text-decoration: underline;
  font-size: 0.9rem;
}

.admin-button:hover {
  color: white;
}

.how-to-section {
  background: white;
  padding: 60px 20px;
  text-align: center;
}

.how-to-section h2 {
  font-size: 2.5rem;
  color: #333;
  margin-bottom: 3rem;
}

.steps-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  max-width: 1000px;
  margin: 0 auto;
}

.step {
  padding: 2rem;
  border-radius: 15px;
  background: #f8f9fa;
  transition: transform 0.3s ease;
}

.step:hover {
  transform: translateY(-5px);
}

.step-number {
  width: 60px;
  height: 60px;
  background: linear-gradient(45deg, #667eea, #764ba2);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: bold;
  margin: 0 auto 1rem;
}

.step h3 {
  color: #333;
  margin-bottom: 0.5rem;
}

.step p {
  color: #666;
  line-height: 1.5;
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
  }
  .hero-title-secondary {
    font-size: 1.6rem;
    margin-top: -0.3rem;
  }
  
  .hero-subtitle {
    font-size: 1.2rem;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>