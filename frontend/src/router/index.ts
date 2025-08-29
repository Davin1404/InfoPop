import { createRouter, createWebHistory } from 'vue-router'
import ChatBox from '../components/ChatBox.vue'
import FileUpload from '../components/FileUpload.vue'

const routes = [
  {
    path: '/',
    name: 'Chat',
    component: ChatBox
  },
  {
    path: '/upload',
    name: 'FileUpload',
    component: FileUpload
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
