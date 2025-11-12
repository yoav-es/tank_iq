<script setup lang="ts">
import { FuelEntryDB } from '../types/FuelEntry';
import { computed } from 'vue';

// Define Props: receives a single, complete fuel entry object
const props = defineProps<{
  entry: FuelEntryDB;
}>();

// Define Events: emits events up to the parent component (FuelLogView)
const emit = defineEmits<{
  (e: 'edit', entry: FuelEntryDB): void;
  (e: 'delete', id: number): void;
}>();

// --- Computed Properties for Display Formatting ---

const formatNumber = (value: number, decimals: number = 2) => {
  if (typeof value !== 'number') return 'N/A';
  return value.toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
};

const totalCost = computed(() => formatNumber(props.entry.total_cost));
const pricePerLiter = computed(() => formatNumber(props.entry.price_per_liter, 3));
const kmPerLiter = computed(() => formatNumber(props.entry.km_per_liter));
const liters = computed(() => formatNumber(props.entry.liters));

// --- Handlers ---

const handleEdit = () => {
  // Emit the full entry object to the parent for modal display
  emit('edit', props.entry);
};

const handleDelete = () => {
  // Emit only the ID for the parent to process the delete action
  emit('delete', props.entry.id);
};
</script>

<template>
  <div class="entry-card bg-white p-5 rounded-xl shadow-md border border-gray-100 hover:shadow-lg transition duration-150">
    
    <div class="flex justify-between items-center border-b pb-2 mb-3">
      <h4 class="text-xl font-bold text-gray-800">
        🗓️ {{ entry.date }}
      </h4>
      <span class="text-sm font-medium text-gray-500">
        Entry #{{ entry.id }}
      </span>
    </div>

    <div class="grid grid-cols-2 gap-4 text-gray-700 mb-4">
      
      <div class="col-span-2 sm:col-span-1 bg-blue-50 p-3 rounded-lg flex justify-between items-center border-l-4 border-blue-500">
        <span class="font-medium">KM/L Efficiency</span>
        <span class="text-2xl font-extrabold text-blue-700">{{ kmPerLiter }}</span>
      </div>

      <div class="col-span-2 sm:col-span-1 bg-green-50 p-3 rounded-lg flex justify-between items-center border-l-4 border-green-500">
        <span class="font-medium">Total Cost (C)</span>
        <span class="text-2xl font-extrabold text-green-700">{{ totalCost }}</span>
      </div>

      <div class="flex justify-between">
        <span class="text-sm font-medium">Distance (KM)</span>
        <span class="font-semibold">{{ formatNumber(entry.distance) }}</span>
      </div>
      
      <div class="flex justify-between">
        <span class="text-sm font-medium">Price / Liter (C)</span>
        <span class="font-semibold">{{ pricePerLiter }}</span>
      </div>

      <div class="flex justify-between">
        <span class="text-sm font-medium">Liters Filled</span>
        <span class="font-semibold">{{ liters }}</span>
      </div>

    </div>

    <p v-if="entry.notes" class="text-sm text-gray-600 italic border-t pt-3 mt-3">
      Notes: {{ entry.notes }}
    </p>

    <div class="flex justify-end space-x-3 border-t pt-3 mt-3">
      <button 
        @click="handleEdit"
        class="text-sm px-3 py-1 bg-yellow-100 text-yellow-700 rounded-md hover:bg-yellow-200 transition duration-150 font-medium"
      >
        Edit
      </button>
      <button 
        @click="handleDelete"
        class="text-sm px-3 py-1 bg-red-100 text-red-700 rounded-md hover:bg-red-200 transition duration-150 font-medium"
      >
        Delete
      </button>
    </div>
  </div>
</template>

<style scoped>
/* Scoped styles for the card */
</style>