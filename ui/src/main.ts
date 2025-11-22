// ui/src/main.ts
import { createApp } from 'vue';
import { createPinia } from 'pinia';
import naive from 'naive-ui';
import App from './App.vue';
import router from './router';
import { useLayoutStore } from './stores/layout-store';
import './main.css';

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);
app.use(naive);

// ✅ Apply persisted layout state safely
useLayoutStore(pinia).init();

app.mount('#app');