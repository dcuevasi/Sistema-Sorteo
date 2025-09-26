import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Register from '../views/Register.vue'
import EmailVerification from '../views/EmailVerification.vue'
import AdminLogin from '../views/AdminLogin.vue'
import AdminParticipants from '../views/AdminParticipants.vue'
import AdminDrawing from '../views/AdminDrawing.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/register',
      name: 'register',
      component: Register
    },
    {
      path: '/verify/:token?',
      name: 'verify',
      component: EmailVerification,
      props: true
    },
    {
      path: '/verify-email',
      name: 'verify-email',
      component: EmailVerification
    },
    {
      path: '/admin/login',
      name: 'admin-login',
      component: AdminLogin
    },
    {
      path: '/admin/participants',
      name: 'admin-participants',
      component: AdminParticipants,
      meta: { requiresAuth: true }
    },
    {
      path: '/admin/drawing',
      name: 'admin-drawing',  
      component: AdminDrawing,
      meta: { requiresAuth: true }
    }
  ]
})

// Rutas protegidas
router.beforeEach((to, from, next) => {
  if (to.matched.some(record => record.meta.requiresAuth)) {
    const token = localStorage.getItem('adminToken')
    if (!token) {
      next({ name: 'admin-login' })
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router