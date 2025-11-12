// ui/src/router/index.ts

import { createRouter, createWebHistory, RouteLocationNormalized } from 'vue-router';
//                                         ^^^^^^^^^^^^^^^^^^^^^ Required for TypeScript error fix

// 1. Define Route Components (using lazy loading)
const FuelLogView = () => import('../views/FuelLogView.vue');
const StatsView = () => import('../views/StatsView.vue');
const EntryFormView = () => import('../views/EntryFormView.vue');

// 2. Define the Routes
const routes = [
  {
    path: '/',
    name: 'Home',
    component: FuelLogView,
  },
  {
    path: '/stats',
    name: 'Stats',
    component: StatsView,
  },
  // Route for adding a new entry
  {
    path: '/entry/add',
    name: 'AddEntry',
    component: EntryFormView,
    props: { isEdit: false }, 
  },
  // Route for editing an existing entry, uses dynamic ID segment
  {
    path: '/entry/edit/:id(\\d+)', // The :id must be a digit
    name: 'EditEntry',
    component: EntryFormView,
    // FIX for ts(7006): Explicitly type the route parameter
    props: (route: RouteLocationNormalized) => ({ 
      isEdit: true, 
      entryId: Number(route.params.id) // Ensure ID is passed as a number
    }),
  },
];

// 3. Create the Router Instance
const router = createRouter({
  // Use HTML5 history mode (clean URLs)
  history: createWebHistory(),
  routes,
});

export default router;