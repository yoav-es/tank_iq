<!-- ui/src/App.vue -->
<template>
  <div id="app">
    <div class="app-layout">
      <!-- Sidebar -->
      <aside class="sidebar">
        <h2 class="sidebar__title">{{ appTitle }}</h2>
        <nav>
          <ul class="sidebar__list">
            <li class="sidebar__item">
              <router-link
                to="/dashboard"
                class="sidebar__link"
                active-class="sidebar__link--active"
              >
                <n-icon size="18">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8v-10h-8v10zm0-18v6h8V3h-8z" />
                  </svg>
                </n-icon>
                <span>Dashboard</span>
              </router-link>
            </li>
            <li class="sidebar__item">
              <router-link
                to="/stats"
                class="sidebar__link"
                active-class="sidebar__link--active"
              >
                <n-icon size="18">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M3 17h2v-7H3v7zm4 0h2V7H7v10zm4 0h2v-4h-2v4zm4 0h2V4h-2v13zm4 0h2v-9h-2v9z" />
                  </svg>
                </n-icon>
                <span>Statistics</span>
              </router-link>
            </li>
            <li class="sidebar__item">
              <router-link
                to="/log"
                class="sidebar__link"
                active-class="sidebar__link--active"
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
      <main
        class="content"
        :class="{ 'content--no-scroll': $route.name === 'Dashboard' }"
      >
        <router-view />
      </main>
    </div>

    <!-- Footer -->
    <footer class="footer">
      <button class="footer__button" @click="toggleDarkMode">
        Dark Mode
      </button>
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
/* ==========================================================================
   App layout (scoped to App.vue)
   ========================================================================== */

.app-layout {
  flex: 1;
  display: grid;
  grid-template-columns: clamp(100px, 12vw, 160px) 1fr;
  min-height: 0; /* allow content to scroll */
}

/* Sidebar */
.sidebar {
  background: var(--color-sidebar-bg);
  padding: var(--space-md);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
}

.sidebar__title {
  color: var(--color-secondary);
  margin-bottom: var(--space-md);
}

.sidebar__list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.sidebar__item {
  margin-bottom: var(--space-md);
}

.sidebar__link {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-sm);
  text-decoration: none;
  color: var(--color-text);
  transition: background-color var(--transition-fast), color var(--transition-fast);
}

.sidebar__link:hover {
  background-color: var(--color-surface);
}

.sidebar__link--active {
  background-color: var(--color-secondary);
  color: var(--color-surface-strong, #111827); /* fallback */
  font-weight: 600;
}

/* Content */
.content {
  background: var(--color-content);
  padding: var(--space-lg);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.content--no-scroll {
  overflow-y: hidden;
}

/* Footer */
.footer {
  flex-shrink: 0;
  display: flex;
  justify-content: center;
  gap: var(--space-md);
  padding: var(--space-xs) var(--space-sm);
  background: var(--color-footer-bg);
  font-size: var(--font-size-xs);
  box-shadow: 0 -1px 4px rgba(0, 0, 0, 0.3);
}

.footer__button {
  background: transparent;
  border: none;
  color: var(--color-text);
  cursor: pointer;
  transition: color var(--transition-fast);
  font-size: var(--font-size-sm);
  padding: var(--space-xs) var(--space-sm);
}

.footer__button:hover {
  color: var(--color-secondary);
}

/* Responsive */
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