<!-- ui/src/app.vue -->
<template>
  <div id="app">
    <div class="app-layout">
      <!-- Sidebar -->
      <aside class="sidebar">
        <h2 class="app-title">{{ appTitle }}</h2>
        <nav>
          <ul>
            <li>
              <router-link
                to="/dashboard"
                :class="{ active: $route.name === 'Dashboard' }"
              >
                <n-icon size="18">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8v-10h-8v10zm0-18v6h8V3h-8z"/>
                  </svg>
                </n-icon>
                <span>Dashboard</span>
              </router-link>
            </li>
            <li>
              <router-link
                to="/stats"
                :class="{ active: $route.name === 'Stats' }"
              >
                <n-icon size="18">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M3 17h2v-7H3v7zm4 0h2V7H7v10zm4 0h2v-4h-2v4zm4 0h2V4h-2v13zm4 0h2v-9h-2v9z"/>
                  </svg>
                </n-icon>
                <span>Statistics</span>
              </router-link>
            </li>
            <li>
              <router-link
                to="/log"
                :class="{ active: $route.name === 'Log' }"
              >
                <n-icon size="18">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M3 5v14h18V5H3zm16 12H5V7h14v10z"/>
                  </svg>
                </n-icon>
                <span>Log</span>
              </router-link>
            </li>
          </ul>
        </nav>
      </aside>

      <!-- Main Content -->
      <main class="content" :class="{ 'no-scroll': $route.name === 'Dashboard' }">
        <router-view />
      </main>
    </div>

    <!-- Footer -->
    <footer class="footer">
      <button>Quick Links</button>
      <button @click="exportCsv">Export CSV</button>
      <button @click="toggleDarkMode">Dark Mode</button>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { useLayoutStore } from './stores/layout-store';

const appTitle = 'TankIQ';
const layoutStore = useLayoutStore();

function exportCsv(): void {
  // Hook into your backend /entries/export/ endpoint
  // For now, just a placeholder
  // eslint-disable-next-line no-alert
  alert('Export CSV triggered');
}

function toggleDarkMode(): void {
  layoutStore.toggleSidebar(); // or implement a dark mode toggle in layoutStore
}
</script>

<style scoped>
.app-layout {
  display: grid;
  grid-template-columns: clamp(100px, 12vw, 160px) 1fr;
  min-height: 100vh;
}

.sidebar {
  background: var(--color-sidebar-bg);
  color: var(--color-sidebar-text);
  padding: var(--space-md);
  position: sticky;
  top: 0;
  height: 100vh;
}

.sidebar ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.sidebar li {
  margin-bottom: var(--space-md);
}

.sidebar .active {
  font-weight: bold;
  color: var(--color-accent);
}

.content {
  background: var(--color-main-bg);
  padding: var(--space-lg);
  overflow-y: auto;
}

.content.no-scroll {
  overflow-y: hidden;
}

.footer {
  display: flex;
  justify-content: space-around;
  padding: var(--space-md);
  background: var(--color-footer-bg);
}
</style>