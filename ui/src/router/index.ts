// ui/src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router';
import type { RouteRecordRaw } from 'vue-router';

import DashboardView from '../views/DashboardView.vue';
import StatsView from '../views/StatsView.vue';
import LogView from '../views/LogView.vue';

/**
 * Application routes definition.
 * Each route maps a path to a view component.
 */
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/dashboard', // default redirect
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
    redirect: '/dashboard', // catch-all fallback
  },
];

/**
 * Create and export Vue Router instance.
 * Uses HTML5 history mode for clean URLs.
 */
export default createRouter({
  history: createWebHistory(),
  routes,
});
