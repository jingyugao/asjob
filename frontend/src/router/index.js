import { createRouter, createWebHistory } from 'vue-router'
import DatabaseManager from '../views/DatabaseManager.vue'
import Chat from '../views/Chat.vue'

const routes = [
  {
    path: '/',
    redirect: '/database'
  },
  {
    path: '/database',
    name: 'DatabaseManager',
    component: DatabaseManager
  },
  {
    path: '/chat',
    name: 'Chat',
    component: Chat
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
