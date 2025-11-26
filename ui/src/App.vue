<!-- ui/src/App.vue -->
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
                    <path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8v-10h-8v10zm0-18v6h8V3h-8z" />
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
                    <path d="M3 17h2v-7H3v7zm4 0h2V7H7v10zm4 0h2v-4h-2v4zm4 0h2V4h-2v13zm4 0h2v-9h-2v9z" />
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
                    <path d="M3 5v14h18V5H3zm16 12H5V7h14v10z" />
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
      <button @click="toggleDarkMode">Dark Mode</button>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { useLayoutStore } from './stores/layout-store';

const appTitle: string = 'TankIQ';
const layoutStore = useLayoutStore();

function exportCsv(): void {
  alert('Export CSV triggered');
}

function toggleDarkMode(): void {
  alert('Dark mode toggle clicked (not implemented yet)');
}
</script>

<style scoped>
/* Root app layout */
#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh; /* ensures footer sits at bottom */
  font-family: 'Inter', system-ui, sans-serif;
  background-color: var(--color-background);
  color: var(--color-text);
}

/* Layout */
.app-layout {
  flex: 1; /* fills space above footer */
  display: grid;
  grid-template-columns: clamp(100px, 12vw, 160px) 1fr;
  min-height: 0; /* allow content to scroll */
}

/* Sidebar */
.sidebar {
  background: var(--color-sidebar-bg);
  color: var(--color-text);
  padding: var(--space-md);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
}

.sidebar h2 {
  color: var(--color-secondary);
  margin-bottom: var(--space-md);
}

.sidebar ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.sidebar li {
  margin-bottom: var(--space-md);
}

.sidebar a {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  border-radius: 6px;
  text-decoration: none;
  color: var(--color-text);
  transition: background-color 0.2s ease, color 0.2s ease;
}

.sidebar a:hover {
  background-color: var(--color-surface);
}

.sidebar a.active {
  background-color: var(--color-secondary);
  color: #111827;
  font-weight: bold;
}

/* Content Area */
.content {
  background: var(--color-content);
  padding: var(--space-lg);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  color: var(--color-text);
}

.content.no-scroll {
  overflow-y: hidden;
}

/* Footer */
.footer {
  flex-shrink: 0; /* prevents shrinking */
  display: flex;
  justify-content: center;
  gap: var(--space-md);
  padding: 0.1rem 0.25rem;  
  background: var(--color-footer-bg);
  color: var(--color-text);
  font-size: 0.5rem;
  box-shadow: 0 -1px 4px rgba(0,0,0,0.3);
}

.footer button {
  background: transparent;
  border: none;
  color: var(--color-text);
  cursor: pointer;
  transition: color 0.2s ease;
  font-size: 0.75rem;
  padding: 0.1rem 0.25rem;
}

.footer button:hover {
  color: var(--color-secondary);
}

/* Responsive Layout */
@media (max-width: 768px) {
  .app-layout {
    grid-template-columns: 1fr;
  }

  .sidebar {
    width: 100%;
    height: auto;
    position: relative;
    border-right: none;
    border-bottom: 1px solid var(--color-border);
  }
}
</style>