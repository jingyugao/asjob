import { createRouter, createWebHistory } from 'vue-router'
import DatabaseManager from '../views/DatabaseManager.vue'

const routes = [
  {
    path: '/',
    redirect: '/database'
  },
  {
    path: '/database',
    name: 'DatabaseManager',
    component: DatabaseManager
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
