<script setup lang="ts">
import { onMounted, computed } from 'vue';
import { useFuelStore } from '../stores/fuelStore';
import StatsCard from '../components/StatsCard.vue'; // Component to be created in Task 6

// --- 1. Store and Data Fetching ---
const store = useFuelStore();

onMounted(() => {
  // Fetch detailed stats only if they haven't been loaded yet
  if (!store.detailedStats) {
    store.fetchDetailedStats();
  }
});

// --- 2. State Access and Computed Properties ---

const detailedStats = computed(() => store.detailedStats);
const isLoading = computed(() => store.isLoading);
const error = computed(() => store.error);

// Compute the monthly stats for display
const monthlyStats = computed(() => detailedStats.value?.monthly_stats || []);
// Compute the yearly stats for display
const yearlyStats = computed(() => detailedStats.value?.yearly_stats || []);

</script>

<template>
  <div class="stats-view container mx-auto p-4">
    <h1 class="text-3xl font-bold mb-6 text-gray-800">📊 Detailed Fuel Statistics</h1>

    <div v-if="isLoading" class="text-center p-8">
      <p class="text-xl text-blue-500">Calculating detailed statistics...</p>
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mt-4"></div>
    </div>

    <div v-else-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
      <strong class="font-bold">Error:</strong>
      <span class="block sm:inline ml-2">{{ error }}</span>
    </div>

    <div v-else-if="!detailedStats || (monthlyStats.length === 0 && yearlyStats.length === 0)" class="text-center p-8 bg-gray-50 rounded-lg shadow-inner">
      <p class="text-xl text-gray-600">No data available to generate statistics.</p>
      <router-link to="/" class="mt-4 inline-block text-blue-600 hover:text-blue-800 transition duration-150">
        Go back to Fuel Log
      </router-link>
    </div>

    <div v-else class="space-y-10">

      <div>
        <h2 class="text-2xl font-semibold mb-4 text-gray-700 border-b pb-2">Monthly Breakdown</h2>
        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          <StatsCard 
            v-for="stats in monthlyStats" 
            :key="stats.period_label" 
            :stats="stats" 
            :title="stats.period_label" 
          />
        </div>
      </div>

      <div>
        <h2 class="text-2xl font-semibold mb-4 text-gray-700 border-b pb-2">Yearly Summaries</h2>
        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          <StatsCard 
            v-for="stats in yearlyStats" 
            :key="stats.period_label" 
            :stats="stats" 
            :title="stats.period_label" 
          />
        </div>
      </div>
      
    </div>
  </div>
</template>

<style scoped>
/* Scoped styles */
</style>