<!-- ui/src/App.vue -->
<template>
  <div id="app">
    <div class="app-layout">
      <!-- Sidebar -->
      <aside class="sidebar">
        <h2 class="sidebar__title">{{ appTitle }}</h2>
        <nav>
          <ul class="sidebar__list">
            <li
              v-for="item in navItems"
              :key="item.to"
              class="sidebar__item"
            >
              <router-link
                :to="item.to"
                class="sidebar__link"
                active-class="sidebar__link--active"
              >
                <n-icon size="18">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path :d="item.iconPath" />
                  </svg>
                </n-icon>
                <span>{{ item.label }}</span>
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
      <span class="footer__brand">TankIQ by Yoav‑ES || Version 1.0.0 || </span>
      <button class="footer__button" @click="toggleDarkMode">
        {{ isDark ? 'Light Mode' : 'Dark Mode' }}
      </button>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useLayoutStore } from './stores/layout-store';

const appTitle = 'TankIQ';
const layoutStore = useLayoutStore();
const isDark = ref(false);

// Sidebar navigation items
const navItems = [
  {
    to: '/dashboard',
    label: 'Dashboard',
    iconPath: 'M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8v-10h-8v10zm0-18v6h8V3h-8z'
  },
  {
    to: '/stats',
    label: 'Statistics',
    iconPath: 'M3 17h2v-7H3v7zm4 0h2V7H7v10zm4 0h2v-4h-2v4zm4 0h2V4h-2v13zm4 0h2v-9h-2v9z'
  },
  {
    to: '/log',
    label: 'Log',
    iconPath: 'M3 5v14h18V5H3zm16 12H5V7h14v10z'
  }
];

function toggleDarkMode(): void {
  isDark.value = !isDark.value;
  layoutStore.toggleDarkMode?.(); // call store action if implemented
  document.documentElement.classList.toggle('dark', isDark.value);
}
</script>

<style scoped>
/* ==========================================================================
   App layout (scoped to App.vue)
   ========================================================================== */
#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
.app-layout {
  flex: 1;
  display: grid;
  grid-template-columns: clamp(100px, 12vw, 160px) 1fr;
  min-height: 0;
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
  color: var(--color-surface-strong, #111827);
  font-weight: 600;
}

/* Content */
.content {
  background: var(--color-content);
  padding: var(--space-lg);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  padding-bottom: 48px;
}

.content--no-scroll {
  overflow-y: hidden;
}

/* Footer */
.footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: var(--color-footer-bg);
  color: var(--color-text);
  border-top: 1px solid var(--color-border);

  display: flex;
  justify-content: center; /* center everything together */
  gap: var(--space-md);    
  align-items: center;              /* vertical centering */
  padding: 0 var(--space-md);       /* horizontal breathing room */
  height: 36px;                     /* slightly taller for comfort */
  font-size: var(--font-size-sm);
  box-shadow: 0 -2px 4px rgba(0,0,0,0.05); /* subtle shadow for depth */
}

.footer__brand {
  font-weight: 500;
  color: var(--color-text);
  opacity: 0.8;                     /* softer look */
}

.footer__button {
  background-color: var(--color-secondary);
  color: #fff;
  border-radius: var(--radius-sm);
  padding: var(--space-xs) var(--space-md);
  font-size: var(--font-size-sm);
  font-weight: 500;
  cursor: pointer;
  transition: background-color var(--transition-fast),
              transform var(--transition-fast);
}

.footer__button:hover {
  background-color: var(--color-secondary-hover);
  transform: translateY(-1px);      /* subtle lift on hover */
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
