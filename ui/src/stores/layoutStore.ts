// ui/src/stores/layoutStore.ts
import { defineStore } from 'pinia';

/**
 * State interface for layout store.
 * Tracks sidebar visibility, selected menu, and dark mode preference.
 */
interface LayoutState {
  sidebarOpen: boolean;
  selectedMenu: string;
  darkMode: boolean;
}

/**
 * LocalStorage key for persisting layout state.
 */
const STORAGE_KEY = 'layoutState';

/**
 * Pinia store for managing application layout state.
 * Provides actions for initializing, persisting, and toggling UI preferences.
 */
export const useLayoutStore = defineStore('layout', {
  state: (): LayoutState => ({
    sidebarOpen: false,   // sidebar starts closed
    selectedMenu: 'entries',
    darkMode: false,      // start in light mode
  }),

  actions: {
    /**
     * Initialize layout state from localStorage.
     * Applies persisted values if available.
     */
    init(): void {
      try {
        const raw = localStorage.getItem(STORAGE_KEY);
        if (!raw) return;
        const parsed = JSON.parse(raw) as Partial<LayoutState>;

        if (typeof parsed.sidebarOpen === 'boolean') {
          this.sidebarOpen = parsed.sidebarOpen;
        }
        if (typeof parsed.selectedMenu === 'string') {
          this.selectedMenu = parsed.selectedMenu;
        }
        if (typeof parsed.darkMode === 'boolean') {
          this.darkMode = parsed.darkMode;
          document.documentElement.classList.toggle('dark', this.darkMode);
        }
      } catch (err) {
        console.warn('Failed to load layout state from localStorage:', err);
      }
    },

    /**
     * Persist current layout state to localStorage.
     */
    persist(): void {
      try {
        localStorage.setItem(
          STORAGE_KEY,
          JSON.stringify({
            sidebarOpen: this.sidebarOpen,
            selectedMenu: this.selectedMenu,
            darkMode: this.darkMode,
          }),
        );
      } catch (err) {
        console.warn('Failed to persist layout state:', err);
      }
    },

    /**
     * Toggle sidebar open/closed state.
     */
    toggleSidebar(): void {
      this.sidebarOpen = !this.sidebarOpen;
      this.persist();
    },

    /**
     * Set sidebar open/closed explicitly.
     */
    setSidebar(open: boolean): void {
      this.sidebarOpen = open;
      this.persist();
    },

    /**
     * Set selected menu key.
     */
    setMenu(key: string): void {
      this.selectedMenu = key;
      this.persist();
    },

    /**
     * Toggle dark mode preference.
     * Updates document class and persists state.
     */
    toggleDarkMode(): void {
      this.darkMode = !this.darkMode;
      document.documentElement.classList.toggle('dark', this.darkMode);
      this.persist();
    },
  },
});
