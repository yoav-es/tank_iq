// ui/src/stores/fuel-store.ts
import { defineStore } from 'pinia';
import {
  FuelEntryDB,
  FuelEntryInput,
  OverallStats,
  DetailedStats,
} from '../types/FuelEntry';
import * as apiService from '../services/api-service';

/**
 * State interface for fuel store.
 */
interface FuelState {
  entries: FuelEntryDB[];
  overallStats: OverallStats | null;
  detailedStats: DetailedStats | null;
  isLoadingEntries: boolean;
  isLoadingStats: boolean;
  error: string | null;
  lastUpdated: number;
}

/**
 * Pinia store for managing fuel entries and statistics.
 * Provides actions for CRUD operations, stats fetching, purge/export, and bulk import.
 */
export const useFuelStore = defineStore('fuel', {
  state: (): FuelState => ({
    entries: [],
    overallStats: null,
    detailedStats: null,
    isLoadingEntries: false,
    isLoadingStats: false,
    error: null,
    lastUpdated: 0,
  }),

  getters: {
    /**
     * Indicates whether entries and overall stats are loaded.
     */
    isDataLoaded: (state): boolean =>
      state.entries.length > 0 && state.overallStats !== null,
  },

  actions: {
    /**
     * Fetch entries and overall stats from backend.
     */
    async fetchEntriesAndStats(): Promise<void> {
      this.isLoadingEntries = true;
      this.error = null;
      try {
        const { entries, overall_stats } = await apiService.getEntries();
        this.entries = entries;
        this.overallStats = overall_stats;
        this.lastUpdated = Date.now();
      } catch (err: unknown) {
        this.error = err instanceof Error ? err.message : 'Unknown error';
        this.entries = [];
        this.overallStats = null;
      } finally {
        this.isLoadingEntries = false;
      }
    },

    /**
     * Add a new entry and refresh stats.
     */
    async addEntry(newEntryData: FuelEntryInput): Promise<FuelEntryDB> {
      try {
        const createdEntry = await apiService.createEntry(newEntryData);
        this.entries.unshift(createdEntry);
        await this.fetchEntriesAndStats();
        return createdEntry;
      } catch (err: unknown) {
        this.error = err instanceof Error ? err.message : 'Unknown error';
        throw err;
      }
    },

    /**
     * Update an existing entry and refresh stats.
     */
    async updateExistingEntry(id: number, updatedData: FuelEntryInput): Promise<FuelEntryDB> {
      try {
        const updatedEntry = await apiService.updateEntry(id, updatedData);
        const index = this.entries.findIndex((entry) => entry.id === id);
        if (index !== -1) {
          this.entries[index] = updatedEntry;
        }
        await this.fetchEntriesAndStats();
        return updatedEntry;
      } catch (err: unknown) {
        this.error = err instanceof Error ? err.message : 'Unknown error';
        throw err;
      }
    },

    /**
     * Remove an entry and refresh stats.
     */
    async removeEntry(id: number): Promise<void> {
      try {
        await apiService.deleteEntry(id);
        this.entries = this.entries.filter((entry) => entry.id !== id);
        await this.fetchEntriesAndStats();
      } catch (err: unknown) {
        this.error = err instanceof Error ? err.message : 'Unknown error';
        throw err;
      }
    },

    /**
     * Fetch detailed statistics from backend.
     */
    async fetchDetailedStats(): Promise<void> {
      this.isLoadingStats = true;
      this.error = null;
      try {
        const stats = await apiService.getDetailedStats();
        this.detailedStats = stats;
        this.lastUpdated = Date.now();
      } catch (err: unknown) {
        this.error = err instanceof Error ? err.message : 'Unknown error';
        this.detailedStats = null;
      } finally {
        this.isLoadingStats = false;
      }
    },

    /**
     * Purge all entries from backend and reset local state.
     */
    async clearAllEntries(): Promise<void> {
      try {
        await apiService.purgeEntries();
        this.entries = [];
        this.overallStats = null;
        this.detailedStats = null;
        this.lastUpdated = Date.now();
      } catch (err: unknown) {
        this.error = err instanceof Error ? err.message : 'Unknown error';
        throw err;
      }
    },

    /**
     * Export entries as CSV string.
     */
    async exportEntriesCsv(): Promise<string> {
      try {
        const csv = await apiService.exportEntriesCsv();
        return csv;
      } catch (err: unknown) {
        this.error = err instanceof Error ? err.message : 'Unknown error';
        throw err;
      }
    },

    /**
     * Bulk import entries sequentially.
     * @returns Number of successfully imported entries
     */
    async bulkImport(entriesToImport: FuelEntryInput[]): Promise<number> {
      let importedCount = 0;
      for (const entry of entriesToImport) {
        try {
          await this.addEntry(entry);
          importedCount++;
        } catch (err) {
          console.error('Failed to import entry:', entry, err);
        }
      }
      return importedCount;
    },
  },
});
