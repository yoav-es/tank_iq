<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useFuelStore } from '../stores/fuelStore';
import { FuelEntryInput, FuelEntryDB } from '../types/FuelEntry';

// --- 1. Props Definition ---
// isEdit determines if we are adding (false) or editing (true)
// entryId is only present if isEdit is true
const props = defineProps<{
  isEdit: boolean;
  entryId?: number;
}>();

// --- 2. Store and Router Setup ---
const store = useFuelStore();
const router = useRouter();

// --- 3. Reactive Form State ---

// Default state for a new entry
const defaultFormState: FuelEntryInput = {
  date: new Date().toISOString().substring(0, 10), // Current date in YYYY-MM-DD format
  liters: 0,
  price_per_liter: 0,
  distance: 0,
  notes: null,
};

// Form data is mutable
const formData = ref<FuelEntryInput>({ ...defaultFormState });
const formError = ref<string | null>(null);
const isLoading = ref(false);

// --- 4. Logic for Editing Existing Entry ---

onMounted(() => {
  if (props.isEdit && props.entryId) {
    // Look up the existing entry in the store's current list
    const existingEntry = store.entries.find(e => e.id === props.entryId);
    
    if (existingEntry) {
      // Copy the existing entry data into the form for editing
      formData.value = {
        date: existingEntry.date,
        liters: existingEntry.liters,
        price_per_liter: existingEntry.price_per_liter,
        distance: existingEntry.distance,
        notes: existingEntry.notes,
      };
    } else {
      // If entry not found (e.g., direct link or deleted), redirect to home
      router.push({ name: 'Home' });
      store.error = `Entry ID ${props.entryId} not found.`;
    }
  }
});

// --- 5. Computed Properties ---

const pageTitle = computed(() => 
  props.isEdit ? `✏️ Edit Entry #${props.entryId}` : '➕ Add New Fuel Entry'
);

const submitButtonText = computed(() => 
  props.isEdit ? 'Save Changes' : 'Record Entry'
);

// Basic validation for form fields
const isFormValid = computed(() => {
  return formData.value.liters > 0 &&
         formData.value.price_per_liter > 0 &&
         formData.value.distance > 0 &&
         !!formData.value.date;
});

// --- 6. Form Submission Handler ---

const handleSubmit = async () => {
  if (!isFormValid.value) {
    formError.value = 'Please ensure Date, Liters, Price, and Distance are greater than zero.';
    return;
  }

  isLoading.value = true;
  formError.value = null;

  try {
    const entryData = formData.value;
    
    if (props.isEdit && props.entryId) {
      // Handle UPDATE operation
      await store.updateExistingEntry(props.entryId, entryData);
    } else {
      // Handle CREATE operation
      await store.addEntry(entryData);
    }

    // Success: Redirect back to the home page (Fuel Log View)
    router.push({ name: 'Home' });

  } catch (err: any) {
    // Error feedback from the store action
    formError.value = `Submission failed: ${store.error || 'Check console for details.'}`;
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <div class="entry-form-view container mx-auto p-4 max-w-lg">
    <h1 class="text-3xl font-bold mb-6 text-gray-800">{{ pageTitle }}</h1>

    <div v-if="formError" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
      <strong class="font-bold">Error:</strong>
      <span class="block sm:inline ml-2">{{ formError }}</span>
    </div>

    <form @submit.prevent="handleSubmit" class="bg-white p-6 rounded-lg shadow-xl space-y-4">
      
      <div>
        <label for="date" class="block text-sm font-medium text-gray-700">Date</label>
        <input 
          id="date"
          type="date"
          v-model="formData.date"
          required
          :disabled="isLoading"
          class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
        />
      </div>

      <div>
        <label for="liters" class="block text-sm font-medium text-gray-700">Liters Fueled</label>
        <input 
          id="liters"
          type="number"
          step="0.01"
          v-model.number="formData.liters"
          required
          min="0.01"
          :disabled="isLoading"
          class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
        />
      </div>

      <div>
        <label for="price_per_liter" class="block text-sm font-medium text-gray-700">Price Per Liter (Currency)</label>
        <input 
          id="price_per_liter"
          type="number"
          step="0.001"
          v-model.number="formData.price_per_liter"
          required
          min="0.001"
          :disabled="isLoading"
          class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
        />
      </div>

      <div>
        <label for="distance" class="block text-sm font-medium text-gray-700">Distance Travelled (KM)</label>
        <input 
          id="distance"
          type="number"
          v-model.number="formData.distance"
          required
          min="1"
          :disabled="isLoading"
          class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
        />
      </div>

      <div>
        <label for="notes" class="block text-sm font-medium text-gray-700">Notes (Optional)</label>
        <textarea 
          id="notes"
          v-model="formData.notes"
          :disabled="isLoading"
          rows="3"
          class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
        ></textarea>
      </div>

      <div class="flex justify-between pt-4">
        <button 
          type="button" 
          @click="router.back()" 
          :disabled="isLoading"
          class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 transition duration-150"
        >
          Cancel
        </button>
        
        <button 
          type="submit"
          :disabled="!isFormValid || isLoading"
          :class="['px-6 py-2 text-sm font-bold text-white rounded-md transition duration-150 shadow-md', 
                   isFormValid && !isLoading ? 'bg-green-600 hover:bg-green-700' : 'bg-green-300 cursor-not-allowed']"
        >
          <span v-if="isLoading">Processing...</span>
          <span v-else>{{ submitButtonText }}</span>
        </button>
      </div>
    </form>
  </div>
</template>

<style scoped>
/* Scoped styles */
</style>