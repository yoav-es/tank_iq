<script setup lang="ts">
import { computed } from 'vue';
import { OverallStats, TimePeriodStats } from '../types/FuelEntry';

// Define props:
// 1. stats: Can be either OverallStats or TimePeriodStats
// 2. title: The label for the card (e.g., "Overall Lifetime" or "2024-07")
const props = defineProps<{
  stats: OverallStats | TimePeriodStats;
  title: string;
}>();

// --- Computed Properties for Display Formatting ---

const formatNumber = (value: number, decimals: number = 2) => {
  return value.toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
};

const totalCost = computed(() => {
  return formatNumber(props.stats.total_cost);
});

const avgKmPerLiter = computed(() => {
  return formatNumber(props.stats.average_km_per_liter);
});

const avgCostPerLiter = computed(() => {
  return formatNumber(props.stats.average_cost_per_liter, 3);
});

const totalDistance = computed(() => {
  return formatNumber(props.stats.total_distance);
});
</script>

<template>
  <div class="stats-card bg-white p-6 rounded-xl shadow-lg border border-gray-100">
    <h3 class="text-xl font-semibold mb-4 text-gray-800 border-b pb-2 flex justify-between items-center">
      <span>{{ title }}</span>
      <span v-if="'count' in stats" class="text-sm font-normal text-gray-500">
        ({{ stats.count }} fill-ups)
      </span>
    </h3>

    <dl class="space-y-3 text-gray-700">
      
      <div class="flex justify-between items-center border-b pb-2">
        <dt class="text-lg font-medium text-blue-600 flex items-center">
          <span class="mr-2">🛣️</span> Average KM/L
        </dt>
        <dd class="text-2xl font-bold text-blue-700">{{ avgKmPerLiter }}</dd>
      </div>

      <div class="flex justify-between items-center">
        <dt class="font-medium">Total Distance (KM)</dt>
        <dd class="font-semibold">{{ totalDistance }}</dd>
      </div>
      
      <div class="flex justify-between items-center">
        <dt class="font-medium">Total Cost (Currency)</dt>
        <dd class="font-semibold text-green-600">{{ totalCost }}</dd>
      </div>
      
      <div class="flex justify-between items-center">
        <dt class="font-medium">Avg Cost / Liter</dt>
        <dd class="font-semibold">{{ avgCostPerLiter }}</dd>
      </div>

      <div class="flex justify-between items-center">
        <dt class="font-medium">Total Liters</dt>
        <dd class="font-semibold">{{ formatNumber(stats.total_liters) }}</dd>
      </div>
      
    </dl>
  </div>
</template>

<style scoped>
/* Scoped styles for the card */
</style>