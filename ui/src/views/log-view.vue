<!-- ui/src/views/log-view.vue -->
<template>
  <section class="log">
    <h1>Fuel Log</h1>

    <!-- Controls -->
    <div class="controls">
      <label>
        Sort:
        <select v-model="sortOrder">
          <option value="newest">Newest First</option>
          <option value="oldest">Oldest First</option>
        </select>
      </label>
      <label>
        Filter:
        <input v-model="filterText" placeholder="Search notes..." />
      </label>
    </div>

    <!-- Entries Table -->
    <table>
      <thead>
        <tr>
          <th>Date</th>
          <th>Distance</th>
          <th>Liters</th>
          <th>Total Cost</th>
          <th>Efficiency (km/L)</th>
          <th>Notes</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="entry in visibleEntries" :key="entry.id">
          <td>{{ entry.date }}</td>
          <td>{{ entry.distance }}</td>
          <td>{{ entry.liters }}</td>
          <td>{{ entry.total_cost }}</td>
          <td>{{ entry.km_per_liter }}</td>
          <td>{{ entry.notes }}</td>
          <td>
            <button @click="onEditEntry(entry)">Edit</button>
            <button @click="onDeleteEntry(entry.id)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>
  </section>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useFuelStore } from '../stores/fuel-store';
import type { FuelEntryDB } from '../types/fuel-entry';

const fuelStore = useFuelStore();

const sortOrder = ref<'newest' | 'oldest'>('newest');
const filterText = ref('');

onMounted(async () => {
  await fuelStore.fetchEntriesAndStats();
});

const filteredEntries = computed<FuelEntryDB[]>(() => {
  if (!filterText.value) return fuelStore.entries;
  return fuelStore.entries.filter((e) =>
    e.notes?.toLowerCase().includes(filterText.value.toLowerCase())
  );
});

const sortedEntries = computed<FuelEntryDB[]>(() => {
  const list = [...filteredEntries.value];
  list.sort((a, b) => {
    const da = a.date ? new Date(a.date).getTime() : 0;
    const db = b.date ? new Date(b.date).getTime() : 0;
    return sortOrder.value === 'newest' ? db - da : da - db;
  });
  return list;
});

const visibleEntries = computed(() => sortedEntries.value);

function onEditEntry(entry: FuelEntryDB) {
  // implement edit logic
  console.log('Edit entry', entry);
}

function onDeleteEntry(id: number) {
  // implement delete logic
  console.log('Delete entry', id);
}
</script>

<style scoped>
.log {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.controls {
  display: flex;
  gap: var(--space-md);
  margin-bottom: var(--space-md);
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: var(--space-sm);
  border-bottom: 1px solid var(--color-border);
}

tbody tr:nth-child(odd) {
  background-color: var(--color-row-light);
}

tbody tr:nth-child(even) {
  background-color: var(--color-row-dark);
}

tbody tr:hover {
  background-color: var(--color-row-hover);
}
</style>