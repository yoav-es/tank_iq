<!-- ui/src/views/log-view.vue -->
<template>
  <section class="log">
    <h1>Fuel Log</h1>

    <!-- Add Entry Form -->
    <form class="add-form" @submit.prevent="onAddEntry">
      <input v-model="newEntry.date" type="date" required />
      <input v-model.number="newEntry.distance" placeholder="Distance (km)" />
      <input v-model.number="newEntry.liters" placeholder="Liters" />
      <input v-model.number="newEntry.price_per_liter" placeholder="Price per Liter" />
      <input v-model="newEntry.notes" placeholder="Notes" />
      <button type="submit" class="add-btn">➕ Add Entry</button>
    </form>

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
          <th>Price/L</th>
          <th>Total Cost</th>
          <th>Efficiency (km/L)</th>
          <th>Notes</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="entry in visibleEntries" :key="entry.id">
          <td v-if="editingId !== entry.id">{{ entry.date }}</td>
          <td v-else><input v-model="editData.date" type="date" /></td>

          <td v-if="editingId !== entry.id">{{ entry.distance }}</td>
          <td v-else><input v-model.number="editData.distance" /></td>

          <td v-if="editingId !== entry.id">{{ entry.liters }}</td>
          <td v-else><input v-model.number="editData.liters" /></td>

          <td v-if="editingId !== entry.id">{{ entry.price_per_liter }}</td>
          <td v-else><input v-model.number="editData.price_per_liter" /></td>

          <td>{{ entry.total_cost }}</td>
          <td>{{ entry.km_per_liter }}</td>

          <td v-if="editingId !== entry.id">{{ entry.notes }}</td>
          <td v-else><input v-model="editData.notes" /></td>

          <td>
            <button v-if="editingId !== entry.id" @click="startEdit(entry)">Edit</button>
            <button v-else @click="saveEdit(entry.id)">Save</button>
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
import type { FuelEntryDB, FuelEntryInput } from '../types/fuel-entry';

const fuelStore = useFuelStore();

const sortOrder = ref<'newest' | 'oldest'>('newest');
const filterText = ref('');

const newEntry = ref<FuelEntryInput>({
  date: null,
  distance: null as any,
  liters: null as any,
  price_per_liter: null as any,
  notes: null
});


const editingId = ref<number | null>(null);
const editData = ref<Partial<FuelEntryDB>>({});

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

async function onAddEntry() {
  try {
    await fuelStore.addEntry(newEntry.value);
    newEntry.value = { date: '', distance: 0, liters: 0, price_per_liter: 0, notes: '' };
  } catch (err) {
    console.error('Failed to add entry', err);
  }
}

function startEdit(entry: FuelEntryDB) {
  editingId.value = entry.id;
  editData.value = { ...entry };
}

async function saveEdit(id: number) {
  try {
    await fuelStore.updateExistingEntry(id, editData.value as FuelEntryInput);
    editingId.value = null;
    editData.value = {};
  } catch (err) {
    console.error('Failed to update entry', err);
  }
}

async function onDeleteEntry(id: number) {
  try {
    await fuelStore.removeEntry(id);
  } catch (err) {
    console.error('Failed to delete entry', err);
  }
}
</script>

<style scoped>
.log {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.add-form {
  display: flex;
  gap: var(--space-md);
  margin-bottom: var(--space-md);
}

.add-btn {
  background-color: var(--color-accent);
  color: white;
  padding: var(--space-sm) var(--space-md);
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.add-btn:hover {
  background-color: var(--color-accent-hover);
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