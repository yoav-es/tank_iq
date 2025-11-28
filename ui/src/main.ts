// ui/src/main.ts
import { createApp } from 'vue';
import { createPinia } from 'pinia';
import naive from 'naive-ui';
import App from './App.vue';
import router from './router';
import { useLayoutStore } from './stores/layout-store';
import './main.css';

// 🔑 Chart.js v4 registration
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  BarElement,
  CategoryScale,
  LinearScale,
  PointElement
} from 'chart.js';

// Register the components you use (line + bar charts, scales, plugins)
ChartJS.register(
  Title,
  Tooltip,
  Legend,
  LineElement,
  BarElement,
  CategoryScale,
  LinearScale,
  PointElement
);

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);
app.use(naive);

// ✅ Apply persisted layout state safely
useLayoutStore(pinia).init();

app.mount('#app');
