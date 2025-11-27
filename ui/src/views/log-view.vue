<!-- ui/src/views/log-view.vue -->
<!-- ui/src/views/log-view.vue -->
<template>
  <section class="log">
    <h1 class="log__headline">Log</h1>

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
          <input v-model="newEntry.date" type="date" required class="log__input" />
        </div>
        <div class="log__field">
          <label class="log__label">Distance (km)</label>
          <input v-model.number="newEntry.distance" type="number" step="0.01" class="log__input" />
        </div>
        <div class="log__field">
          <label class="log__label">Liters</label>
          <input v-model.number="newEntry.liters" type="number" step="0.01" class="log__input" />
        </div>
        <div class="log__field">
          <label class="log__label">Price per Liter</label>
          <input v-model.number="newEntry.price_per_liter" type="number" step="0.01" class="log__input" />
        </div>
        <div class="log__field">
          <label class="log__label">Notes</label>
          <input v-model="newEntry.notes" type="text" class="log__input" />
        </div>
      </div>

      <button type="submit" class="log__add-btn">Add Entry</button>
    </form>

    <!-- Controls -->
    <div class="log__controls">
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

      <div class="log__control">
        <label>
          Filter by notes:
          <input v-model="filterText" placeholder="Search notes..." class="input" />
        </label>
      </div>
    </div>

    <!-- Entries Table -->
    <table class="log__table">
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
              class="log__edit-btn"
            >
              Edit
            </button>
            <button
              v-else
              @click="saveEdit(entry.id)"
              class="log__save-btn"
            >
              Save
            </button>
            <button
              @click="onDeleteEntry(entry.id)"
              class="log__delete-btn"
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
          <button @click="onPurgeDatabase" class="button button--danger">Purge ✖</button>
        </div>
      </div>
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
// -------------------- Export CSV --------------------
function onExportCsv(): void {
  const header = "date,distance,liters,price_per_liter,notes\n";
  const rows = fuelStore.entries.map(e =>
    `${e.date},${e.distance},${e.liters},${e.price_per_liter},${e.notes || ""}`
  );
  const csvContent = header + rows.join("\n");

  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", "fuel_log.csv");
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  showFeedback("CSV exported successfully!", "success");
}

// -------------------- Purge Database --------------------
async function onPurgeDatabase(): Promise<void> {
  if (!confirm("Are you sure you want to delete ALL entries?")) return;
  try {
    await fuelStore.clearAllEntries(); // implement in your store
    showFeedback("All entries removed successfully!", "success");
  } catch (err) {
    console.error("Failed to purge database", err);
    showFeedback("Failed to purge database.", "error");
  }
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
/* ==========================================================================
   Log view
   ========================================================================== */

.log {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

/* Headline */
.log__headline {
  font-size: var(--font-size-xl);
  font-weight: 600;
  margin-bottom: var(--space-sm);
  color: var(--color-text-strong);
  border-bottom: 2px solid var(--color-border);
  padding-bottom: var(--space-xs);
}

/* Add Entry Form */
.log__add-form {
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

.log__input {
  width: 100%;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: var(--space-xs) var(--space-sm);
  font-size: var(--font-size-md);
  background-color: var(--color-input-bg);
  color: var(--color-text);
}

/* Add Entry button */
.log__add-btn {
  align-self: flex-start;
  background-color: var(--color-success);
  color: #fff;
  font-weight: 500;
  margin-top: var(--space-xs);
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  padding: var(--space-sm) var(--space-md);
  font-size: var(--font-size-md);
  transition: background-color var(--transition-fast);
}
.log__add-btn:hover {
  background-color: var(--color-success-hover);
}
.log__add-btn:disabled {
  background-color: var(--color-border);
  cursor: not-allowed;
}

/* Controls */
.log__controls {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-md);
  margin-bottom: var(--space-sm);
}

.log__control {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  white-space: nowrap;
}

.log__control .select,
.log__control .input {
  min-width: 160px;
  height: 2rem;
  padding: 0 var(--space-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-md);
  background-color: var(--color-surface);
  color: var(--color-text);
}

.log__control .select option {
  background-color: var(--color-input-bg);
  color: var(--color-text);
}

/* Action buttons */
.log__actions {
  display: flex;
  gap: var(--space-sm);
}

.log__edit-btn {
  background-color: var(--color-primary);
}
.log__edit-btn:hover {
  background-color: var(--color-primary-hover);
}

.log__save-btn {
  background-color: var(--color-secondary);
}
.log__save-btn:hover {
  background-color: var(--color-secondary-hover);
}

.log__delete-btn {
  background-color: var(--color-danger);
}
.log__delete-btn:hover {
  background-color: var(--color-danger-hover);
}

/* Table */
.log__table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: var(--space-xs);
  border-bottom: 1px solid var(--color-border);
}

.log__table th {
  text-align: left;
  font-weight: 600;
  color: var(--color-text-strong);
}

.log__table th,
.log__table td {
  padding: var(--space-sm);
  border-bottom: 1px solid var(--color-border);
}

.log__table tbody tr:nth-child(odd) {
  background-color: var(--color-row-light);
}
.log__table tbody tr:nth-child(even) {
  background-color: var(--color-row-dark);
}
.log__table tbody tr:hover {
  background-color: var(--color-row-hover);
  transition: background-color var(--transition-fast);
}

/* Bulk Import */
.log__csv-import {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
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

.log__csv-import input[type="file"] {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: var(--space-xs);
  background-color: var(--color-input-bg);
  color: var(--color-text);
  width: auto;
  flex: 0 0 auto;
  min-width: unset;
}

/* Feedback */
.feedback {
  position: fixed;
  top: 1rem;
  right: 1rem;
  z-index: var(--z-toast);
  padding: 0.75rem 1rem;
  border-radius: var(--radius-sm);
  font-weight: 500;
  box-shadow: var(--shadow-sm);
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  color: var(--color-text);
}

.feedback--success {
  background-color: #e6ffed;
  color: #1a7f37;
  border-color: #1a7f37;
}

.feedback--error {
  background-color: #ffe6e6;
  color: #a71d2a;
  border-color: #a71d2a;
}

/* Fade transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--transition-slow);
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
