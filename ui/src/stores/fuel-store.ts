// ui/src/stores/fuel-store.ts
import { defineStore } from 'pinia';
import {
  FuelEntryDB,
  FuelEntryInput,
  OverallStats,
  DetailedStats,
} from '../types/fuel-entry';
import * as apiService from '../services/api-service';

interface FuelState {
  entries: FuelEntryDB[];
  overallStats: OverallStats | null;
  detailedStats: DetailedStats | null;
  // CHANGE: split loading into two flags
  isLoadingEntries: boolean;   // CHANGE: new
  isLoadingStats: boolean;     // CHANGE: new
  error: string | null;
  // CHANGE: track last update timestamp for freshness
  lastUpdated: number;         // CHANGE: new
}

export const useFuelStore = defineStore('fuel', {
  state: (): FuelState => ({
    entries: [],
    overallStats: null,
    detailedStats: null,
    // CHANGE: initialize new flags
    isLoadingEntries: false,   // CHANGE: new
    isLoadingStats: false,     // CHANGE: new
    error: null,
    lastUpdated: 0,            // CHANGE: new
  }),

  getters: {
    isDataLoaded: (state): boolean =>
      state.entries.length > 0 && state.overallStats !== null,
  },

  actions: {
    async fetchEntriesAndStats(): Promise<void> {
      this.isLoadingEntries = true; // CHANGE: use specific flag
      this.error = null;
      try {
        const { entries, overall_stats } = await apiService.getEntries(); // CHANGE: removed timestamp
        this.entries = entries;
        this.overallStats = overall_stats;
      } catch (err: unknown) {
        this.error = err instanceof Error ? err.message : 'Unknown error';
        this.entries = [];
        this.overallStats = null;
      } finally {
        this.isLoadingEntries = false; // CHANGE: reset specific flag
      }
    },

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

    async fetchDetailedStats(): Promise<void> {
      // CHANGE: use isLoadingStats instead of isLoading
      this.isLoadingStats = true;
      this.error = null;
      try {
        const stats = await apiService.getDetailedStats();
        this.detailedStats = stats;
      } catch (err: unknown) {
        this.error = err instanceof Error ? err.message : 'Unknown error';
        this.detailedStats = null;
      } finally {
        // CHANGE: reset isLoadingStats
        this.isLoadingStats = false;
      }
    },
        // Purge all entries
    async clearAllEntries(): Promise<void> {
      try {
        // Call backend to delete everything
        await apiService.purgeEntries();

        // Reset local state
        this.entries = [];
        this.overallStats = null;
        this.detailedStats = null;

        // Optionally refresh to confirm backend state
        // await this.fetchEntriesAndStats();
      } catch (err: unknown) {
        this.error = err instanceof Error ? err.message : 'Unknown error';
        throw err;
      }
    },

    // Export CSV from backend (optional)
    async exportEntriesCsv(): Promise<string> {
      try {
        const csv = await apiService.exportEntriesCsv();
        return csv;
      } catch (err: unknown) {
        this.error = err instanceof Error ? err.message : 'Unknown error';
        throw err;
      }
    }
  },
});