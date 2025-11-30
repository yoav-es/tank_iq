<!-- ui/src/views/log-view.vue -->
<!-- ui/src/views/log-view.vue -->
<template>
  <section class="log">
    <h1 class="headline">📊 Log</h1>

    <!-- Feedback message block -->
    <transition name="fade">
      <p v-if="feedbackMessage" :class="['feedback', `feedback--${feedbackType}`]">
        {{ feedbackMessage }}
      </p>
    </transition>

    <!-- Add Entry Form -->
    <form class="log__add-form" @submit.prevent="onAddEntry">
      <div class="log__fields">
        <div class="log__field">
          <label class="log__label">Date</label>
          <input v-model="newEntry.date" type="date" required class="input" />
        </div>
        <div class="log__field">
          <label class="log__label">Distance (km)</label>
          <input v-model.number="newEntry.distance" type="number" step="0.01" class="input" />
        </div>
        <div class="log__field">
          <label class="log__label">Liters</label>
          <input v-model.number="newEntry.liters" type="number" step="0.01" class="input" />
        </div>
        <div class="log__field">
          <label class="log__label">Price per Liter</label>
          <input v-model.number="newEntry.price_per_liter" type="number" step="0.01" class="input" />
        </div>
        <div class="log__field">
          <label class="log__label">Notes</label>
          <input v-model="newEntry.notes" type="text" class="input" />
        </div>
      </div>

      <!-- Button aligned left -->
      <div class="u-flex u-align-start">
        <button type="submit" class="button button--primary">Add Entry</button>
      </div>
    </form>

    <div class="log__controls">
      <!-- Left side: Sort -->
      <div class="log__control">
        <label>
          Sort:
          <select v-model="sortField" class="select">
            <option value="date">Date</option>
            <option value="distance">Distance</option>
            <option value="liters">Liters</option>
            <option value="price_per_liter">Price/L</option>
            <option value="total_cost">Total Cost</option>
            <option value="km_per_liter">Efficiency</option>
          </select>
          <select v-model="sortOrder" class="select">
            <option value="newest">Descending</option>
            <option value="oldest">Ascending</option>
          </select>
        </label>
      </div>

      <!-- Right side: Filter -->
      <div class="log__control log__control--search">
        <label>
          Filter by notes:
          <input v-model="filterText" placeholder="Search notes..." class="input" />
        </label>
      </div>
    </div>

    <!-- Entries Table -->
    <table class="table">
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
          <td v-if="editingId !== entry.id">{{ formatDate(entry.date) }}</td>
          <td v-else><input v-model="editData.date" type="date" class="input" /></td>

          <td v-if="editingId !== entry.id">{{ entry.distance }}</td>
          <td v-else><input v-model.number="editData.distance" type="number" class="input" /></td>

          <td v-if="editingId !== entry.id">{{ entry.liters }}</td>
          <td v-else><input v-model.number="editData.liters" type="number" class="input" /></td>

          <td v-if="editingId !== entry.id">{{ entry.price_per_liter }}</td>
          <td v-else><input v-model.number="editData.price_per_liter" type="number" step="0.01" class="input" /></td>

          <td>{{ entry.total_cost.toFixed(2) }}</td>
          <td>{{ entry.km_per_liter.toFixed(2) }}</td>

          <td v-if="editingId !== entry.id">{{ entry.notes }}</td>
          <td v-else><input v-model="editData.notes" type="text" class="input" /></td>

          <td class="log__actions">
            <button
              v-if="editingId !== entry.id"
              @click="startEdit(entry)"
              class="button button--secondary"
            >
              Edit
            </button>
            <button
              v-else
              @click="saveEdit(entry.id)"
              class="button button--primary"
            >
              Save
            </button>
            <button
              @click="onDeleteEntry(entry.id)"
              class="button button--danger"
            >
              Delete
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Bulk Import -->
    <div class="log__csv-import">
      <h2 class="log__csv-title">Bulk Import</h2>
      <p class="log__csv-desc">You can upload a CSV file to add multiple entries at once.</p>
      <p class="log__csv-desc">
        <strong>Required column order:</strong>
        <code>date,distance,liters,price_per_liter,notes</code>
      </p>

      <div class="log__import-row">
        <input type="file" accept=".csv" @change="onCsvUpload" class="input input--file" />
        <div class="log__bulk-actions">
          <button @click="onExportCsv" class="button button--secondary">Export CSV</button>
          <button @click="onPurgeDatabase" class="button button--danger">Purge All Entries</button>
        </div>
      </div>
    </div>
  </section>
</template>



<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useFuelStore } from '../stores/fuelStore';
import { storeToRefs } from 'pinia';
import { formatDate } from '../utils/format';
import type { FuelEntryDB, FuelEntryInput } from '../types/FuelEntry';

// Composables & utils
import { useFeedback } from '../composables/useFeedback';
import { useEntries } from '../composables/useEntries';
import { parseCsvRows, toCsv, downloadCsv } from '../utils/csv';
import { emptyEntry } from '../types/FuelEntry';

// -------------------- Store --------------------
const fuelStore = useFuelStore();
const { entries } = storeToRefs(fuelStore);
const { feedbackMessage, feedbackType, showFeedback } = useFeedback();

// -------------------- State --------------------
const sortOrder = ref<'newest' | 'oldest'>('newest');
const sortField = ref<'date' | 'distance' | 'liters' | 'price_per_liter' | 'total_cost' | 'km_per_liter'>('date');
const filterText = ref('');

const newEntry = ref<FuelEntryInput>(emptyEntry());
const editingId = ref<number | null>(null);
const editData = ref<FuelEntryInput>(emptyEntry());

// -------------------- Lifecycle --------------------
onMounted(async () => {
  try {
    await fuelStore.fetchEntriesAndStats();
  } catch (err) {
    console.error('Failed to fetch entries', err);
    showFeedback('Failed to load entries.', 'error');
  }
});

// -------------------- Computed --------------------
const { visibleEntries } = useEntries(entries, sortField, sortOrder, filterText);

// -------------------- Actions --------------------
async function onAddEntry(): Promise<void> {
  try {
    await fuelStore.addEntry(newEntry.value);
    newEntry.value = emptyEntry();
    showFeedback('Entry added successfully!', 'success');
  } catch (err) {
    console.error('Failed to add entry', err);
    showFeedback('Failed to add entry.', 'error');
  }
}

function startEdit(entry: FuelEntryDB): void {
  editingId.value = entry.id;
  editData.value = {
    date: entry.date ?? '',
    distance: entry.distance ?? 0,
    liters: entry.liters ?? 0,
    price_per_liter: entry.price_per_liter ?? 0,
    notes: entry.notes ?? ''
  };
}

async function saveEdit(id: number): Promise<void> {
  try {
    await fuelStore.updateExistingEntry(id, editData.value);
    editingId.value = null;
    editData.value = emptyEntry(); // reset only on success
    showFeedback('Entry updated successfully!', 'success');
  } catch (err) {
    console.error('Failed to update entry', err);
    showFeedback('Failed to update entry.', 'error');
    // keep editData populated so user can retry
  }
}

async function onDeleteEntry(id: number): Promise<void> {
  try {
    await fuelStore.removeEntry(id);
    showFeedback('Entry deleted successfully!', 'success');
  } catch (err) {
    console.error('Failed to delete entry', err);
    showFeedback('Failed to delete entry.', 'error');
  }
}

// -------------------- CSV Import --------------------
async function onCsvUpload(event: Event): Promise<void> {
  const input = event.target as HTMLInputElement;
  if (!input.files?.length) return;

  const file = input.files[0];
  const reader = new FileReader();
  reader.onload = async (e) => {
    const text = e.target?.result as string;
    const rows = text.trim().split('\n');

    const headerFields = rows[0].trim().toLowerCase().split(',');
    const expectedFields = ['date', 'distance', 'liters', 'price_per_liter', 'notes'];
    if (headerFields.length !== expectedFields.length ||
        !headerFields.every((f, i) => f === expectedFields[i])) {
      showFeedback(`Invalid CSV format. Expected header: ${expectedFields.join(',')}`, 'error');
      return;
    }

    try {
      const entriesToImport = parseCsvRows(rows);
      const importedCount = await fuelStore.bulkImport(entriesToImport);
      showFeedback(`Imported ${importedCount} entries successfully.`, 'success');
    } catch (err) {
      console.error('Failed to import CSV', err);
      showFeedback('CSV import failed.', 'error');
    } finally {
      input.value = ''; // reset file input so same file can be re‑uploaded
    }
  };

  reader.readAsText(file);
}

// -------------------- Export CSV --------------------
function onExportCsv(): void {
  const rows = entries.value.map(e => ({
    id: e.id,
    date: e.date,
    distance: e.distance,
    liters: e.liters,
    price_per_liter: e.price_per_liter,
    notes: e.notes,
    total_cost: e.total_cost ?? (e.liters && e.price_per_liter ? e.liters * e.price_per_liter : 0),
    km_per_liter: e.km_per_liter ?? (e.distance && e.liters ? e.distance / e.liters : 0)
  }));

  const csvContent = toCsv(rows);
  downloadCsv(csvContent, 'fuel_log.csv');
  showFeedback('CSV exported successfully!', 'success');
}

// -------------------- Purge Database --------------------
async function onPurgeDatabase(): Promise<void> {
  if (!confirm('Are you sure you want to delete ALL entries?')) return;
  try {
    await fuelStore.clearAllEntries();
    showFeedback('All entries removed successfully!', 'success');
  } catch (err) {
    console.error('Failed to purge database', err);
    showFeedback('Failed to purge database.', 'error');
  }
}
</script>

<style scoped>
/* ==========================================================================
   Log view
   ========================================================================== */

.log {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

/* Add Entry Form */
.log__add-form {
  align-self: flex-start;
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
  width: 100%;
  border-bottom: 2px solid var(--color-border);
  padding-bottom: var(--space-sm);
  margin-bottom: var(--space-sm);
}

.log__fields {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-sm);
  width: 100%;
}

.log__field {
  flex: 1 1 200px;
  min-width: 160px;
  display: flex;
  flex-direction: column;
}

.log__label {
  margin-bottom: var(--space-xs);
  font-weight: 500;
  color: var(--color-text);
}

/* Controls wrapper */
.log__controls {
  display: flex;
  justify-content: left;   /* ✅ center both groups */
  align-items: left;
  flex-wrap: nowrap;          /* keep them on one line */
  gap: var(--space-lg);       /* spacing between sort and filter groups */
  margin-bottom: var(--space-sm);
}

.log__control {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  white-space: nowrap;
}

.log__control label {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

/* Sort selectors stay compact */
.log__control select {
  width: auto;
  flex: 0 0 auto;
}

/* Filter input has fixed width to avoid overlap */
.log__control--search input {
  width: 220px;
  flex: 0 0 auto;
}

/* Action buttons wrapper */
.log__actions {
  display: flex;
  gap: var(--space-sm);
}

/* Bulk Import */
.log__csv-import {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
  background-color: var(--color-card); /* ✅ match other views/cards */
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: var(--space-md);
}

.log__import-row {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.log__bulk-actions {
  display: flex;
  gap: var(--space-sm);
}

.log__csv-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  margin-bottom: var(--space-xs);
}

.log__csv-desc {
  margin-bottom: var(--space-xs);
  color: var(--color-text);
}
</style>
