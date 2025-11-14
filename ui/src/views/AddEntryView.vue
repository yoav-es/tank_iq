<template>
  <n-card title="Add Fuel Entry" bordered>
    <n-form :model="form" :rules="rules" ref="formRef" label-width="120px">
      <!-- Date -->
      <n-form-item label="Date" path="date">
        <n-date-picker
          v-model:formatted-value="form.date"
          type="date"
          clearable
          value-format="yyyy-MM-dd"
        />
      </n-form-item>

      <!-- Liters -->
      <n-form-item label="Liters" path="liters">
        <n-input-number v-model:value="form.liters" :min="0" />
      </n-form-item>

      <!-- Price per Liter -->
      <n-form-item label="Price per Liter" path="price_per_liter">
        <n-input-number v-model:value="form.price_per_liter" :min="0" />
      </n-form-item>

      <!-- Distance -->
      <n-form-item label="Distance" path="distance">
        <n-input-number v-model:value="form.distance" :min="0" />
      </n-form-item>

      <!-- Notes -->
      <n-form-item label="Notes" path="notes">
        <n-input v-model:value="form.notes" type="textarea" clearable />
      </n-form-item>

      <!-- Submit -->
      <n-form-item>
        <n-button type="primary" @click="submit">Save Entry</n-button>
      </n-form-item>
    </n-form>
  </n-card>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useFuelStore } from '../stores/fuelStore';
import type { FuelEntryInput } from '../types/fuelEntry';
import type { FormInst } from 'naive-ui';

const router = useRouter();
const store = useFuelStore();

const formRef = ref<FormInst | null>(null);
const form = ref<FuelEntryInput>({
  date: null,              // 👈 will be "YYYY-MM-DD" string
  liters: 0,
  price_per_liter: 0,
  distance: 0,
  notes: '',
});

const rules = {
  date: { required: true, type: 'string', message: 'Please select a date', trigger: ['blur', 'change'] },
  liters: { required: true, type: 'number', message: 'Enter liters', trigger: ['blur', 'change'] },
  price_per_liter: { required: true, type: 'number', message: 'Enter price per liter', trigger: ['blur', 'change'] },
  distance: { required: true, type: 'number', message: 'Enter distance', trigger: ['blur', 'change'] },
};



const submit = () => {
  formRef.value?.validate(async (errors: any) => {
    if (!errors) {
      try {
        console.log('Submitting entry:', form.value);
        await store.addEntry(form.value);
        router.push('/');
      } catch (e) {
        console.error('Failed to add entry:', e);
      }
    } else {
      // 👇 handle validation errors instead of letting them throw
      console.warn('Validation failed:', errors);
    }
  });
};


</script>