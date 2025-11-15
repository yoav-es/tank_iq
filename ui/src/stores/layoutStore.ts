// ui/src/stores/layoutStore.ts

import { defineStore } from 'pinia';

interface LayoutState {
  sidebarOpen: boolean;
  selectedMenu: string;
}

const STORAGE_KEY = 'layoutState';

export const useLayoutStore = defineStore('layout', {
  state: (): LayoutState => ({
    sidebarOpen: false, // start closed by default
    selectedMenu: 'entries',
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
      } catch (err) {
        // eslint-disable-next-line no-console
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
          }),
        );
      } catch (err) {
        // eslint-disable-next-line no-console
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
  },
});