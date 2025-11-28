// ui/src/stores/layoutStore.ts
import { defineStore } from 'pinia';

interface LayoutState {
  sidebarOpen: boolean;
  selectedMenu: string;
  darkMode: boolean;   // add dark mode state
}

const STORAGE_KEY = 'layoutState';

export const useLayoutStore = defineStore('layout', {
  state: (): LayoutState => ({
    sidebarOpen: false, // start closed by default
    selectedMenu: 'entries',
    darkMode: false,    // start in light mode
  }),

  actions: {
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

    toggleSidebar(): void {
      this.sidebarOpen = !this.sidebarOpen;
      this.persist();
    },

    setSidebar(open: boolean): void {
      this.sidebarOpen = open;
      this.persist();
    },

    setMenu(key: string): void {
      this.selectedMenu = key;
      this.persist();
    },

    // NEW: toggle dark mode
    toggleDarkMode(): void {
      this.darkMode = !this.darkMode;
      document.documentElement.classList.toggle('dark', this.darkMode);
      this.persist();
    },
  },
});
