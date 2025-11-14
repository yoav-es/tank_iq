import { createRouter, createWebHistory } from 'vue-router';
import FuelLogView from '../views/FuelLogView.vue';
import AddEntryView from '../views/AddEntryView.vue';
import StatsView from '../views/StatsView.vue';

const routes = [
  { path: '/', component: FuelLogView },
  { path: '/entry/add', component: AddEntryView },
  { path: '/stats', component: StatsView },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
