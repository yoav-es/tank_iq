import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router';
import FuelLogView from '../views/FuelLogView.vue';
import AddEntryView from '../views/AddEntryView.vue';
import StatsView from '../views/StatsView.vue';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'entries',
    component: FuelLogView,
  },
  {
    path: '/entry/add',
    name: 'add-entry',
    component: AddEntryView,
  },
  {
    path: '/stats',
    name: 'stats',
    component: StatsView,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;