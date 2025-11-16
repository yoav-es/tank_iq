// ui/src/stores/fuelStore.ts

import { defineStore } from 'pinia';
import { 
  FuelEntryDB, 
  FuelEntryInput, 
  OverallStats, 
  DetailedStats 
} from '../types/FuelEntry';
import * as apiService from '../services/apiService';

// Define the shape of the store's state
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

  // Getters are used for derived state
  getters: {
    // Simple way to check if data is loaded and ready
    isDataLoaded: (state) => state.entries.length > 0 && state.overallStats !== null,
  },

  // Actions are methods used to change the state (often asynchronously)
  actions: {
    /**
     * Fetches all entries and overall stats via the GET /entries/ endpoint.
     */
    async fetchEntriesAndStats() {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await apiService.getEntries();
        console.log('📦 Entries:', response.entries);
        console.log('📊 Overall Stats:', response.overall_stats);
        this.entries = response.entries;
        this.overallStats = response.overall_stats;
      } catch (err: any) {
        this.error = `Failed to load entries: ${err.message}`;
        this.entries = [];
        this.overallStats = null;
        console.error(err);
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Creates a new entry (POST /entries/) and updates local state.
     */
    async addEntry(newEntryData: FuelEntryInput) {
      this.error = null;
      try {
        // API returns the newly created entry (FuelEntryDB) with ID and calculated fields
        const createdEntry = await apiService.createEntry(newEntryData);
        
        // Update local state and trigger UI refresh
        this.entries.unshift(createdEntry); // Add to the start of the array
        
        // Re-fetch stats to update overall averages (best practice after CRUD operation)
        await this.fetchEntriesAndStats(); 

        return createdEntry;
      } catch (err: any) {
        this.error = `Failed to save entry: ${err.message}`;
        throw err; // Re-throw to allow component to handle specific feedback
      }
    },

    /**
     * Updates an existing entry (PUT /entries/{id}) and updates local state.
     */
    async updateExistingEntry(id: number, updatedData: FuelEntryInput) {
      this.error = null;
      try {
        const updatedEntry = await apiService.updateEntry(id, updatedData);
        
        // Find and replace the old entry in the local array
        const index = this.entries.findIndex(entry => entry.id === id);
        if (index !== -1) {
          this.entries[index] = updatedEntry;
        }

        // Re-fetch stats to update overall averages
        await this.fetchEntriesAndStats(); 

        return updatedEntry;
      } catch (err: any) {
        this.error = `Failed to update entry: ${err.message}`;
        throw err;
      }
    },

    /**
     * Deletes an entry (DELETE /entries/{id}) and updates local state.
     */
    async removeEntry(id: number) {
      this.error = null;
      try {
        await apiService.deleteEntry(id);
        
        // Optimistically update the state: remove the entry from the array
        this.entries = this.entries.filter(entry => entry.id !== id);

        // Re-fetch stats to update overall averages (needed for accurate total counts)
        await this.fetchEntriesAndStats(); 
        
      } catch (err: any) {
        this.error = `Failed to delete entry: ${err.message}`;
        throw err;
      }
    },

    /**
     * Fetches detailed statistics via the GET /stats/ endpoint.
     */
    async fetchDetailedStats() {
      this.isLoading = true;
      this.error = null;
      try {
        this.detailedStats = await apiService.getDetailedStats();
        console.log('📈 Detailed Stats:', this.detailedStats);
      } catch (err: any) {
        this.error = `Failed to load detailed stats: ${err.message}`;
        this.detailedStats = null;
        console.error(err);
      } finally {
        this.isLoading = false;
      }
    },
  },
});