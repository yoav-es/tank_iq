<!--ui\views\FuelLogView.vue-->
<template>
  <n-card title="Fuel Log" bordered>
    <n-data-table :columns="columns" :data="store.entries" striped />
  </n-card>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useFuelStore } from '../stores/fuelStore';

const store = useFuelStore();

onMounted(() => {
  store.fetchEntriesAndStats();
});

const columns = [
  { title: 'Date', key: 'date' },
  { title: 'Liters', key: 'liters' },
  { title: 'Price/L', key: 'price_per_liter' },
  { title: 'Distance', key: 'distance' },
  { title: 'Total Cost', key: 'total_cost' },
  { title: 'Km/L', key: 'km_per_liter' },
  { title: 'Notes', key: 'notes' },
];

</script>