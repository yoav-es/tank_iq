// ui/src/main.ts

import { createApp } from 'vue';
import App from './App.vue';
import router from './router/index';
import { createPinia } from 'pinia';

// CRITICAL: Import the Tailwind CSS file
import './assets/main.css'; 

// Create and configure the app instance
const app = createApp(App);
app.use(createPinia());
app.use(router);

app.mount('#app');