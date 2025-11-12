<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import { FuelEntryDB, FuelEntryInput } from '../types/FuelEntry';
import { useFuelStore } from '../stores/fuelStore';

// --- 1. Props and Events ---
const props = defineProps<{
  isVisible: boolean;
  entry: FuelEntryDB; // The entry object being edited
}>();

const emit = defineEmits<{
  (e: 'close'): void;
}>();

// --- 2. Store and State ---
const store = useFuelStore();
const formError = ref<string | null>(null);
const isLoading = ref(false);

// Use a reactive ref for the form data, initialized with entry's data
const formData = ref<FuelEntryInput>({
  date: props.entry.date,
  liters: props.entry.liters,
  price_per_liter: props.entry.price_per_liter,
  distance: props.entry.distance,
  notes: props.entry.notes,
});

// --- 3. Watcher for Prop Changes ---
// This ensures that if the parent passes a *different* entry prop,
// the form data is updated to reflect the new entry's values.
watch(
  () => props.entry,
  (newEntry) => {
    formData.value = {
      date: newEntry.date,
      liters: newEntry.liters,
      price_per_liter: newEntry.price_per_liter,
      distance: newEntry.distance,
      notes: newEntry.notes,
    };
    formError.value = null; // Clear errors when switching entries
  },
  { deep: true }
);

// --- 4. Computed Properties ---

// Basic validation check
const isFormValid = computed(() => {
  return formData.value.liters > 0 &&
         formData.value.price_per_liter > 0 &&
         formData.value.distance > 0 &&
         !!formData.value.date;
});

// --- 5. Form Submission Handler ---

const handleSubmit = async () => {
  if (!isFormValid.value) {
    formError.value = 'Please ensure all numerical fields are greater than zero.';
    return;
  }

  isLoading.value = true;
  formError.value = null;

  try {
    // Call the store action to update the entry
    await store.updateExistingEntry(props.entry.id, formData.value);
    
    // Success: Close the modal
    emit('close');
  } catch (err: any) {
    // Error feedback
    formError.value = `Update failed: ${store.error || 'Check console for details.'}`;
  } finally {
    isLoading.value = false;
  }
};

const handleClose = () => {
  emit('close');
};
</script>

<template>
  <div v-if="isVisible" class="fixed inset-0 bg-gray-900 bg-opacity-50 flex items-center justify-center z-50 transition-opacity duration-300" @click.self="handleClose">
    
    <div class="bg-white rounded-lg shadow-2xl w-full max-w-md mx-4 p-6 transform transition-transform duration-300 scale-100">
      
      <div class="flex justify-between items-center border-b pb-3 mb-4">
        <h3 class="text-2xl font-bold text-gray-800">Edit Entry #{{ entry.id }}</h3>
        <button @click="handleClose" class="text-gray-400 hover:text-gray-600">
          &times;
        </button>
      </div>

      <div v-if="formError" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4 text-sm" role="alert">
        <strong class="font-bold">Error:</strong>
        <span class="block sm:inline ml-2">{{ formError }}</span>
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        
        <div>
          <label for="date" class="block text-sm font-medium text-gray-700">Date</label>
          <input id="date" type="date" v-model="formData.date" required :disabled="isLoading"
            class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2" />
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label for="liters" class="block text-sm font-medium text-gray-700">Liters</label>
            <input id="liters" type="number" step="0.01" v-model.number="formData.liters" required min="0.01" :disabled="isLoading"
              class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2" />
          </div>
          
          <div>
            <label for="price_per_liter" class="block text-sm font-medium text-gray-700">Price / Liter (C)</label>
            <input id="price_per_liter" type="number" step="0.001" v-model.number="formData.price_per_liter" required min="0.001" :disabled="isLoading"
              class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2" />
          </div>
        </div>

        <div>
          <label for="distance" class="block text-sm font-medium text-gray-700">Distance (KM)</label>
          <input id="distance" type="number" v-model.number="formData.distance" required min="1" :disabled="isLoading"
            class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2" />
        </div>

        <div>
          <label for="notes" class="block text-sm font-medium text-gray-700">Notes (Optional)</label>
          <textarea id="notes" v-model="formData.notes" :disabled="isLoading" rows="2"
            class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"></textarea>
        </div>

        <div class="flex justify-end pt-4 space-x-3">
          <button type="button" @click="handleClose" :disabled="isLoading"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 transition duration-150">
            Cancel
          </button>

          <button type="submit" :disabled="!isFormValid || isLoading"
            :class="['px-6 py-2 text-sm font-bold text-white rounded-md transition duration-150 shadow-md', 
                     isFormValid && !isLoading ? 'bg-green-600 hover:bg-green-700' : 'bg-green-300 cursor-not-allowed']">
            <span v-if="isLoading">Saving...</span>
            <span v-else>Save Changes</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
/* Scoped styles */
</style>