<!-- ui/views/App.vue -->
<template>
  <div id="app">
    <div class="app-layout">
      <aside class="sidebar">
        <div>
          <h2>{{ appTitle }}</h2>
          <nav>
            <ul>
              <li>
                <router-link
                  to="/dashboard"
                  :class="{ active: $route.name === 'dashboard' }"
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
                  :class="{ active: $route.name === 'stats' }"
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
                  :class="{ active: $route.name === 'log' }"
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
        </div>
      </aside>

      <main class="content" :class="{ 'no-scroll': $route.name === 'dashboard' }">
        <router-view />
      </main>
    </div>

    <footer class="footer">
      <button>Quick Links</button>
      <button>Export CSV</button>
      <button>Dark Mode</button>
    </footer>
  </div>
</template>

<script setup lang="ts">
const appTitle = 'TankIQ';
</script>

<style scoped>
#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-layout {
  flex: 1;
  display: flex;
  flex-direction: row;
  min-height: 0;
  align-items: stretch;
}

.sidebar {
  width: clamp(100px, 14vw, 200px);
  background-color: var(--color-sidebar);
  color: var(--color-text);
  padding: var(--space-md);
  display: flex;
  flex-direction: column;
  border-right: 1px solid #2d3748;
}

.sidebar h2 {
  color: #14b8a6;
  margin-bottom: var(--space-md);
}

.sidebar ul {
  list-style: none;
  padding: 0;
}

.sidebar li {
  margin: var(--space-sm) 0;
}

.sidebar a {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  border-radius: 6px;
  text-decoration: none;
  color: var(--color-text);
  background-color: transparent;
  transition: background-color 0.2s ease, color 0.2s ease;
}

.sidebar a:hover {
  background-color: #1f2937;
}

.sidebar a.active {
  background-color: var(--color-secondary);
  color: #111827;
  font-weight: bold;
}

.content {
  flex: 1;
  min-height: 0;
  padding: var(--space-xl);
  background-color: var(--color-content);
  color: var(--color-text);
  overflow-y: auto;              /* default: internal scroll when needed */
  display: flex;
  flex-direction: column;
}

/* Disable internal scroll for dashboard specifically */
.content.no-scroll {
  overflow-y: hidden;
}

.footer {
  flex-shrink: 0;
  background-color: var(--color-footer);
  color: var(--color-text);
  text-align: center;
  padding: var(--space-sm);
  border-top: 1px solid #2d3748;
  display: flex;
  justify-content: center;
  gap: var(--space-md);
}

.footer button {
  background: transparent;
  border: none;
  color: var(--color-text);
  cursor: pointer;
  transition: color 0.2s ease;
}

.footer button:hover {
  color: var(--color-secondary);
}
</style>