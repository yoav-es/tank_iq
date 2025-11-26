<!-- ui/src/views/log-view.vue -->
<template>
  <section class="log">
    <h1>Log</h1>

    <!-- Feedback message block -->
    <transition name="fade">
    <p v-if="feedbackMessage" :class="['feedback', feedbackType]">
      {{ feedbackMessage }}
    </p>
    </transition>

    <!-- Add Entry Form -->
    <form class="add-form" @submit.prevent="onAddEntry">
      <div class="fields">
        <div class="form-field">
          <label>Date</label>
          <input v-model="newEntry.date" type="date" required />
        </div>
        <div class="form-field">
          <label>Distance (km)</label>
          <input v-model.number="newEntry.distance" type="number" step="0.01" />
        </div>
        <div class="form-field">
          <label>Liters</label>
          <input v-model.number="newEntry.liters" type="number" step="0.01" />
        </div>
        <div class="form-field">
          <label>Price per Liter</label>
          <input v-model.number="newEntry.price_per_liter" type="number" step="0.01" />
        </div>
        <div class="form-field">
          <label>Notes</label>
          <input v-model="newEntry.notes" type="text" />
        </div>
      </div>

      <button type="submit" class="add-btn">Add Entry</button>
    </form>

    <!-- Controls -->
    <div class="controls">
      <div class="control">
        <label>
          Sort:
          <select class="ui-select" v-model="sortField">
            <option value="date">Date</option>
            <option value="distance">Distance</option>
            <option value="liters">Liters</option>
            <option value="price_per_liter">Price/L</option>
            <option value="total_cost">Total Cost</option>
            <option value="km_per_liter">Efficiency</option>
          </select>
          <select class="ui-select" v-model="sortOrder">
            <option value="newest">Descending</option>
            <option value="oldest">Ascending</option>
          </select>
        </label>
      </div>

      <div class="control">
        <label>
          Filter by notes:
          <input v-model="filterText" placeholder="Search notes..." />
        </label>
      </div>
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
          <td v-if="editingId !== entry.id">{{ formatDate(entry.date) }}</td>
          <td v-else><input v-model="editData.date" type="date" /></td>

          <td v-if="editingId !== entry.id">{{ entry.distance }}</td>
          <td v-else><input v-model.number="editData.distance" type="number" /></td>

          <td v-if="editingId !== entry.id">{{ entry.liters }}</td>
          <td v-else><input v-model.number="editData.liters" type="number" /></td>

          <td v-if="editingId !== entry.id">{{ entry.price_per_liter }}</td>
          <td v-else><input v-model.number="editData.price_per_liter" type="number" step="0.01" /></td>

          <td>{{ entry.total_cost.toFixed(2) }}</td>
          <td>{{ entry.km_per_liter.toFixed(2) }}</td>

          <td v-if="editingId !== entry.id">{{ entry.notes }}</td>
          <td v-else><input v-model="editData.notes" type="text" /></td>

          <td class="actions">
            <button v-if="editingId !== entry.id" @click="startEdit(entry)" class="edit-btn">Edit</button>
            <button v-else @click="saveEdit(entry.id)" class="save-btn">Save</button>
            <button @click="onDeleteEntry(entry.id)" class="delete-btn">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Bulk Import -->
    <div class="csv-import">
      <h2>Bulk Import</h2>
      <p>You can upload a CSV file to add multiple entries at once.</p>
      <p>
        <strong>Required column order:</strong>
        <code>date,distance,liters,price_per_liter,notes</code>
      </p>
      <input type="file" accept=".csv" @change="onCsvUpload" />
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useFuelStore } from '../stores/fuel-store';
import type { FuelEntryDB, FuelEntryInput } from '../types/fuel-entry';

const fuelStore = useFuelStore();

// -------------------- State --------------------
const sortOrder = ref<'newest' | 'oldest'>('newest');
const sortField = ref<'date' | 'distance' | 'liters' | 'price_per_liter' | 'total_cost' | 'km_per_liter'>('date');
const filterText = ref('');

const newEntry = ref<FuelEntryInput>(emptyEntry());
const editingId = ref<number | null>(null);
const editData = ref<FuelEntryInput>(emptyEntry());

// Feedback state
const feedbackMessage = ref("");
const feedbackType = ref<"success" | "error" | "">("");

// Helper to show feedback and auto‑clear
function showFeedback(message: string, type: "success" | "error") {
  feedbackMessage.value = message;
  feedbackType.value = type;
  setTimeout(() => {
    feedbackMessage.value = "";
    feedbackType.value = "";
  }, 3000); // disappears after 3 seconds
}

// -------------------- Lifecycle --------------------
onMounted(() => fuelStore.fetchEntriesAndStats());

// -------------------- Computed --------------------
const filteredEntries = computed<FuelEntryDB[]>(() =>
  filterText.value
    ? fuelStore.entries.filter((e) =>
        e.notes?.toLowerCase().includes(filterText.value.toLowerCase())
      )
    : fuelStore.entries
);

const sortedEntries = computed<FuelEntryDB[]>(() => {
  const list = [...filteredEntries.value];
  list.sort((a, b) => {
    if (sortField.value === 'date') {
      const da = a.date ? new Date(a.date).getTime() : 0;
      const db = b.date ? new Date(b.date).getTime() : 0;
      return sortOrder.value === 'newest' ? db - da : da - db;
    }
    const av = a[sortField.value] ?? 0;
    const bv = b[sortField.value] ?? 0;
    return sortOrder.value === 'newest'
      ? (bv as number) - (av as number)
      : (av as number) - (bv as number);
  });
  return list;
});

const visibleEntries = computed(() => {
  return sortedEntries.value.slice(0, 5); // show only 5 entries
});

// -------------------- Actions --------------------
async function onAddEntry(): Promise<void> {
  try {
    await fuelStore.addEntry(newEntry.value);
    newEntry.value = emptyEntry();
    showFeedback("Entry added successfully!", "success");
  } catch (err) {
    console.error('Failed to add entry', err);
    showFeedback("Failed to add entry.", "error");
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
    editData.value = emptyEntry();
    showFeedback("Entry updated successfully!", "success");
  } catch (err) {
    console.error('Failed to update entry', err);
    showFeedback("Failed to update entry.", "error");
  }
}

async function onDeleteEntry(id: number): Promise<void> {
  try {
    await fuelStore.removeEntry(id);
    showFeedback("Entry deleted successfully!", "success");
  } catch (err) {
    console.error('Failed to delete entry', err);
    showFeedback("Failed to delete entry.", "error");
  }
}

// -------------------- Helpers --------------------
function formatDate(dateStr?: string | null): string {
  return dateStr ? new Date(dateStr).toLocaleDateString() : '';
}

function emptyEntry(): FuelEntryInput {
  return { date: '', distance: 0, liters: 0, price_per_liter: 0, notes: '' };
}

// -------------------- CSV Import --------------------
function onCsvUpload(event: Event): void {
  const input = event.target as HTMLInputElement;
  if (!input.files?.length) return;

  const file = input.files[0];
  const reader = new FileReader();
  reader.onload = async (e) => {
    const text = e.target?.result as string;
    const rows = text.trim().split('\n');

    // Header validation
    const header = rows[0].trim().toLowerCase();
    const expected = "date,distance,liters,price_per_liter,notes";
    if (header !== expected) {
      showFeedback(`Invalid CSV format. Expected header: ${expected}`, "error");
      return;
    }

    const entries = parseCsvRows(rows);
    let importedCount = 0;
    for (const entry of entries) {
      try {
        await fuelStore.addEntry(entry);
        importedCount++;
      } catch (err) {
        console.error('Failed to import entry:', entry, err);
      }
    }

    showFeedback(`Imported ${importedCount} entries successfully.`, "success");
  };

  reader.readAsText(file);
}

function parseCsvRows(rows: string[]): FuelEntryInput[] {
  // Expecting header row: date,distance,liters,price_per_liter,notes
  return rows.slice(1).map((row) => {
    const [date, distance, liters, price_per_liter, ...notesParts] = row.split(',');
    const notes = notesParts.join(','); // allow commas in notes
    return {
      date: date?.trim() || '',
      distance: Number(distance) || 0,
      liters: Number(liters) || 0,
      price_per_liter: Number(price_per_liter) || 0,
      notes: notes?.trim() || ''
    };
  }).filter((entry) =>
    entry.date &&
    !isNaN(entry.distance) &&
    !isNaN(entry.liters) &&
    !isNaN(entry.price_per_liter)
  );
}
</script>


<style scoped>
/* Layout */
.log {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

/* Headline */
.log h1 {
  font-size: 1.8rem;
  font-weight: 600;
  margin-bottom: var(--space-sm);
  color: var(--color-text-strong);
  border-bottom: 2px solid var(--color-border);
  padding-bottom: var(--space-xs);
}

/* Add Entry Form */
.log .add-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
  width: 100%;
  border-bottom: 2px solid var(--color-border);
  padding-bottom: var(--space-sm);
  margin-bottom: var(--space-sm);
}

.log .fields {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-sm);
  width: 100%;
}

.log .form-field {
  flex: 1 1 200px;
  min-width: 160px;
  display: flex;
  flex-direction: column;
}

.log .form-field > label {
  margin-bottom: var(--space-xs);
  font-weight: 500;
  color: var(--color-text);
}

.log .form-field > input {
  width: 100%;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  padding: var(--space-xs) var(--space-sm);
  font-size: 0.9rem;
  background-color: var(--color-input-bg);
  color: var(--color-text);
}

/* Add Entry button */
.log .add-btn {
  align-self: flex-start;
  background-color: var(--color-success);
  color: #fff;
  font-weight: 500;
  margin-top: var(--space-xs);
}
.log .add-btn:hover { background-color: var(--color-success-hover); }
.log .add-btn:disabled { background-color: var(--color-border); cursor: not-allowed; }

/* Controls */
.log .controls {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-md);
  margin-bottom: var(--space-sm);
}

.log .control {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  white-space: nowrap;
}

.log .control select,
.log .control input {
  min-width: 160px;
  height: 2rem;
  padding: 0 var(--space-sm);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: 0.9rem;
  background-color: var(--color-surface);
  color: var(--color-text);
}

/* Dropdown fix */
.log .control select option {
  background-color: var(--color-input-bg);
  color: var(--color-text);
}

/* Buttons */
.log button {
  border: none;
  border-radius: 4px;
  cursor: pointer;
  padding: var(--space-sm) var(--space-md);
  font-size: 0.9rem;
  transition: background-color 0.2s ease;
  color: #fff;
}
.log button:focus {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.log .edit-btn { background-color: var(--color-primary); }
.log .edit-btn:hover { background-color: var(--color-primary-hover); }
.log .save-btn { background-color: var(--color-secondary); }
.log .save-btn:hover { background-color: var(--color-secondary-hover); }
.log .delete-btn { background-color: var(--color-danger); }
.log .delete-btn:hover { background-color: var(--color-danger-hover); }

/* Table */
.log table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: var(--space-xs);
  border-bottom: 1px solid var(--color-border); /* separator under table */
}

.log th {
  text-align: left;
  font-weight: 600;
  color: var(--color-text-strong);
}

.log th, .log td {
  padding: var(--space-sm);
  border-bottom: 1px solid var(--color-border);
}

.log tbody tr:nth-child(odd) { background-color: var(--color-row-light); }
.log tbody tr:nth-child(even) { background-color: var(--color-row-dark); }
.log tbody tr:hover { background-color: var(--color-row-hover); transition: background-color 0.2s ease; }

.log .actions { display: flex; gap: var(--space-sm); }

/* Bulk Import */
.log .csv-import {
  padding-top: var(--space-xs);
}

.log .csv-import h2 {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: var(--space-xs);
}

.log .csv-import p {
  margin-bottom: var(--space-xs);
  color: var(--color-text);
}

.log .csv-import input[type="file"] {
  border: 1px solid var(--color-border);
  border-radius: 4px;
  padding: var(--space-xs);
  background-color: var(--color-input-bg);
  color: var(--color-text);
}

/* Feedback message styles */
/* Toast-style feedback overlay */
.feedback {
  position: fixed;
  top: 1rem;
  right: 1rem;
  z-index: 1000;
  padding: 0.75rem 1rem;
  border-radius: 4px;
  font-weight: 500;
  box-shadow: 0 2px 6px rgba(0,0,0,0.2);
}

/* Success and error colors */
.feedback.success {
  background-color: #e6ffed;
  color: #1a7f37;
  border: 1px solid #1a7f37;
}
.feedback.error {
  background-color: #ffe6e6;
  color: #a71d2a;
  border: 1px solid #a71d2a;
}

/* Fade transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

</style>