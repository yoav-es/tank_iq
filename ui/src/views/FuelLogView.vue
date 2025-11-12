<script setup lang="ts">
import { onMounted, computed, ref } from 'vue';
import { useFuelStore } from '../stores/fuelStore';
import { FuelEntryDB } from '../types/FuelEntry';

// Corrected Imports (Task 6 Components)
import EntryCard from '../components/EntryCard.vue'; 
import StatsCard from '../components/StatsCard.vue'; 
import EditEntryModal from '../components/EditEntryModal.vue'; 

// --- 1. Store and Data Fetching ---
const store = useFuelStore();

onMounted(() => {
  // Fetch data only if the store is empty (avoids unnecessary API calls on navigation/re-mount)
  if (!store.isDataLoaded) {
    store.fetchEntriesAndStats();
  }
});

// --- 2. State Access and Computed Properties ---

// Access state reactively using computed properties
const entries = computed(() => store.entries);
const overallStats = computed(() => store.overallStats);
const isLoading = computed(() => store.isLoading);
const error = computed(() => store.error);

// --- 3. Entry Edit/Delete Modal Logic ---
const isModalVisible = ref(false);
const entryToEdit = ref<FuelEntryDB | null>(null);

/**
 * Opens the modal to edit a specific entry.
 * @param entry The FuelEntryDB object to be edited.
 */
const openEditModal = (entry: FuelEntryDB) => {
  entryToEdit.value = entry;
  isModalVisible.value = true;
};

/**
 * Closes the modal and resets the entry to edit.
 */
const closeModal = () => {
  isModalVisible.value = false;
  entryToEdit.value = null;
};

// --- 4. Component Action Handlers ---

/**
 * Handles the delete event emitted from the EntryCard component.
 * @param id The ID of the entry to delete.
 */
const handleDelete = async (id: number) => {
  if (confirm('Are you sure you want to delete this entry?')) {
    try {
      await store.removeEntry(id);
      // Success is handled by the store state change (entry disappears from the list)
    } catch (err) {
      // Error handling is managed by the store, but we can log/show a persistent error if needed
    }
  }
};
</script>

<template>
  <div class="fuel-log-view container mx-auto p-4">
    <h1 class="text-3xl font-bold mb-6 text-gray-800">⛽ Fuel Log & Overview</h1>

    <div v-if="isLoading" class="text-center p-8">
      <p class="text-xl text-blue-500">Loading fuel data...</p>
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mt-4"></div>
    </div>

    <div v-else-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
      <strong class="font-bold">Error:</strong>
      <span class="block sm:inline ml-2">{{ error }}</span>
    </div>

    <div v-else-if="entries.length === 0 && !isLoading && overallStats" class="text-center p-8 bg-gray-50 rounded-lg shadow-inner">
      <p class="text-xl text-gray-600">No fuel entries found yet.</p>
      <p class="text-md text-gray-500 mt-2">Use the "Add New Entry" button to get started.</p>
      <router-link to="/entry/add" class="mt-4 inline-block bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded transition duration-150">
        Add New Entry
      </router-link>
    </div>

    <div v-else-if="overallStats" class="grid gap-6">

      <div class="mb-6">
        <StatsCard :stats="overallStats" title="Overall Lifetime Averages" />
      </div>

      <div class="flex justify-between items-center mb-4 border-b pb-2">
        <h2 class="text-2xl font-semibold text-gray-700">Recent Entries ({{ entries.length }})</h2>
        <router-link to="/entry/add" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg transition duration-150 shadow-md">
          + Add New Entry
        </router-link>
      </div>

      <div class="space-y-4">
        <EntryCard 
          v-for="entry in entries" 
          :key="entry.id" 
          :entry="entry" 
          @edit="openEditModal" 
          @delete="handleDelete" 
        />
      </div>
    </div>

    <EditEntryModal 
      v-if="isModalVisible && entryToEdit" 
      :isVisible="isModalVisible"
      :entry="entryToEdit"
      @close="closeModal"
    />
  </div>
</template>

<style scoped>
/* Scoped styles */
</style>