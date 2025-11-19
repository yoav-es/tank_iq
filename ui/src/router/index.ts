//ui/src/router/index
import { createRouter, createWebHistory } from 'vue-router';
import type { RouteRecordRaw } from 'vue-router';

import DashboardView from '../views/dashboard-view.vue';
import StatsView from '../views/stats-view.vue';
import LogView from '../views/log-view.vue';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: DashboardView,
  },
  {
    path: '/stats',
    name: 'Stats',
    component: StatsView,
  },
  {
    path: '/log',
    name: 'Log',
    component: LogView,
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard',
  },
];

export default createRouter({
  history: createWebHistory(),
  routes,
});