// ui/src/main.ts

import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router'; 

// 1. Create the root Vue application instance
const app = createApp(App);

// 2. Install Pinia (State Management)
const pinia = createPinia();
app.use(pinia);

// 3. Install Vue Router
app.use(router);

// 4. Mount the application to the DOM element with the id 'app'
app.mount('#app');