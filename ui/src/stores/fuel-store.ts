// ui/src/stores/fuelStore.ts

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
  isLoading: boolean;
  error: string | null;
}

export const useFuelStore = defineStore('fuel', {
  state: (): FuelState => ({
    entries: [],
    overallStats: null,
    detailedStats: null,
    isLoading: false,
    error: null,
  }),

  getters: {
    isDataLoaded: (state): boolean =>
      state.entries.length > 0 && state.overallStats !== null,
  },

  actions: {
    async fetchEntriesAndStats(): Promise<void> {
      this.isLoading = true;
      this.error = null;
      try {
        const { entries, overall_stats } = await apiService.getEntries();
        this.entries = entries;
        this.overallStats = overall_stats;
      } catch (err: unknown) {
        this.error = err instanceof Error ? err.message : 'Unknown error';
        this.entries = [];
        this.overallStats = null;
      } finally {
        this.isLoading = false;
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
        if (index !== -1) this.entries[index] = updatedEntry;
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
      this.isLoading = true;
      this.error = null;
      try {
        this.detailedStats = await apiService.getDetailedStats();
      } catch (err: unknown) {
        this.error = err instanceof Error ? err.message : 'Unknown error';
        this.detailedStats = null;
      } finally {
        this.isLoading = false;
      }
    },
  },
});