import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import MateChat from '@matechat/core'

import '@devui-design/icons/icomoon/devui-icon.css'; 

import axios from 'axios';
axios.defaults.withCredentials = true; // Enable CORS with credentials  
axios.defaults.baseURL = 'http://localhost:8001'; // Adjust the base URL as needed

createApp(App).use(MateChat).use(router).mount('#app')
