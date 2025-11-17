<!--ui\views\LogView.vue-->
<template>
  <section class="log">
    <!-- Header -->
    <h1>Trip Log</h1>

    <!-- Controls -->
    <div class="controls">
      <button @click="addEntry">Add Entry</button>
      <label>
        Date Range:
        <select v-model="selectedRange">
          <option value="7d">Last 7 days</option>
          <option value="30d">Last 30 days</option>
          <option value="all">All time</option>
        </select>
      </label>
      <label>
        Sort:
        <select v-model="sortOrder">
          <option value="newest">Newest</option>
          <option value="oldest">Oldest</option>
        </select>
      </label>
    </div>

    <!-- Infinite Scroll Table -->
    <div class="log-table" ref="scrollContainer" @scroll="onScroll">
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Distance</th>
            <th>Fuel</th>
            <th>Cost</th>
            <th>Efficiency</th>
            <th>Notes</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="entry in visibleEntries" :key="entry.id">
            <td>{{ entry.date }}</td>
            <td>{{ entry.distance }}</td>
            <td>{{ entry.fuel }}</td>
            <td>{{ entry.cost }}</td>
            <td>{{ entry.efficiency }}</td>
            <td>{{ entry.notes }}</td>
            <td>
              <button @click="editEntry(entry)">Edit</button>
              <button @click="deleteEntry(entry.id)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="loading" class="loading">Loading more entries...</div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const selectedRange = ref('all');
const sortOrder = ref('newest');
const entries = ref([
  { id: 1, date: '2025-11-01', distance: 45, fuel: 3.2, cost: 4.6, efficiency: '7.1 L/100km', notes: 'City drive' },
  { id: 2, date: '2025-11-02', distance: 60, fuel: 4.0, cost: 5.8, efficiency: '6.6 L/100km', notes: 'Highway trip' },
  // ... more entries
]);

// Infinite scroll state
const visibleEntries = ref(entries.value.slice(0, 10));
const loading = ref(false);

function onScroll(e: Event) {
  const target = e.target as HTMLElement;
  if (target.scrollTop + target.clientHeight >= target.scrollHeight - 10 && !loading.value) {
    loadMore();
  }
}

function loadMore() {
  loading.value = true;
  setTimeout(() => {
    const currentLength = visibleEntries.value.length;
    const more = entries.value.slice(currentLength, currentLength + 10);
    visibleEntries.value = [...visibleEntries.value, ...more];
    loading.value = false;
  }, 500); // simulate async fetch
}

function addEntry() {
  alert('Add entry form goes here');
}

function editEntry(entry: any) {
  alert(`Edit entry ${entry.id}`);
}

function deleteEntry(id: number) {
  entries.value = entries.value.filter(e => e.id !== id);
  visibleEntries.value = visibleEntries.value.filter(e => e.id !== id);
}
</script>

<style scoped>
.log {
  display: flex;
  flex-direction: column;
  gap: var(--space-2xl);
}

.controls {
  display: flex;
  gap: var(--space-md);
  align-items: center;
}

.log-table {
  max-height: 400px; /* scrollable area */
  overflow-y: auto;
  border: 1px solid #2d3748;
  border-radius: 6px;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: var(--space-sm);
  border-bottom: 1px solid #2d3748;
}

/* darker alternating row colors */
tbody tr:nth-child(odd) {
  background-color: #374151; /* dark slate gray */
  color: #f3f4f6;            /* light text for contrast */
}

tbody tr:nth-child(even) {
  background-color: #1f2937; /* slightly darker gray */
  color: #f3f4f6;
}

tbody tr:hover {
  background-color: #4b5563; /* hover highlight */
}

.loading {
  text-align: center;
  padding: var(--space-md);
  color: #9ca3af;
}
</style>