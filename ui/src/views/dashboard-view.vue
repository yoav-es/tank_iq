<!-- ui/src/views/dashboard-view.vue -->
<template>
  <section class="dashboard">
    <h1 class="view__headline">📊Dashboard</h1>

    <!-- Toggle Buttons -->
    <div class="dashboard__toggle-buttons">
      <button
        class="button button--primary"
        :class="{ 'button--primary': viewMode === 'month' }"
        @click="viewMode = 'month'"
      >
        Monthly
      </button>
      <button
        class="button button--primary"
        :class="{ 'button--primary': viewMode === 'year' }"
        @click="viewMode = 'year'"
      >
        Yearly
      </button>
    </div>

    <!-- Graph Section -->
    <div class="card dashboard__graph-card">
      <h3 class="dashboard__graph-title">Average Fuel Efficiency (km/L)</h3>
      <canvas ref="chartRef"></canvas>
    </div>

    <!-- Stats Grid -->
    <div class="dashboard__cards-grid">
      <div class="card dashboard__stat-card">
        <h3>Current Avg</h3>
        <p>
          {{ fuelStore.overallStats?.average_km_per_liter?.toFixed(2) ?? '—' }} km/L
        </p>
      </div>

      <div class="card dashboard__stat-card">
        <h3>Best {{ viewMode === 'month' ? 'Month' : 'Year' }}</h3>
        <p>
          {{
            viewMode === 'month'
              ? fuelStore.detailedStats?.overall_stats.best_month_efficiency?.toFixed(2) ?? '—'
              : fuelStore.detailedStats?.overall_stats.best_year_efficiency?.toFixed(2) ?? '—'
          }} km/L
        </p>
      </div>

      <div class="card dashboard__stat-card">
        <h3>Total Distance</h3>
        <p>{{ fuelStore.overallStats?.total_distance?.toFixed(1) ?? '—' }} km</p>
      </div>

      <div class="card dashboard__stat-card">
        <h3>Total Cost</h3>
        <p>{{ fuelStore.overallStats?.total_cost?.toFixed(2) ?? '—' }} ₪</p>
      </div>

      <div class="card dashboard__stat-card">
        <h3>Trips Logged</h3>
        <p>{{ fuelStore.overallStats?.entry_count ?? '—' }}</p>
      </div>

      <div class="card dashboard__stat-card">
        <h3>Avg Cost/L</h3>
        <p>{{ fuelStore.overallStats?.average_cost_per_liter?.toFixed(2) ?? '—' }} ₪/L</p>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, shallowRef, onMounted, onUnmounted, watch, nextTick } from 'vue';
import type { Chart } from 'chart.js';
import { useFuelStore } from '../stores/fuel-store';
import {
  Mode,
  getStats,
  initDashboardChart,
  updateDashboardChart
} from '../composables/useChart';

const fuelStore = useFuelStore();
const chartRef = ref<HTMLCanvasElement | null>(null);
const chartInstance = shallowRef<Chart<'line'> | null>(null);
const viewMode = ref<Mode>('month');

onMounted(async () => {
  await fuelStore.fetchEntriesAndStats();
  await fuelStore.fetchDetailedStats();
  await nextTick();
  if (chartRef.value) {
    const stats = getStats(fuelStore.detailedStats, viewMode.value);
    chartInstance.value = initDashboardChart(chartRef.value, viewMode.value, stats);
  }
});

onUnmounted(() => {
  chartInstance.value?.destroy();
  chartInstance.value = null;
});

watch(viewMode, async () => {
  await nextTick();
  if (chartRef.value && chartInstance.value) {
    const stats = getStats(fuelStore.detailedStats, viewMode.value);
    updateDashboardChart(chartInstance.value, viewMode.value, stats);
  }
});
</script>

<style scoped>
/* ==========================================================================
   Dashboard page
   ========================================================================== */

.dashboard {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

/* Toggle buttons wrapper */
.dashboard__toggle-buttons {
  display: flex;
  gap: var(--space-sm);
}

/* Headline */
.dashboard__headline {
  font-size: var(--font-size-xl);
  font-weight: 600;
  color: var(--color-text-strong);
  padding-bottom: var(--space-xs);
  border-bottom: 2px solid var(--color-border);
  margin-bottom: var(--space-xs);
}

/* Graph card */
.dashboard__graph-card {
  background: var(--color-card);
  padding: var(--space-md);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  height: 26.5rem;
  min-height: 27.5rem;
  overflow: hidden;
}

/* Stats grid */
.dashboard__cards-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-sm);
}

/* Stat card */
.dashboard__stat-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  text-align: center;
  font-weight: 700;
  box-shadow: var(--shadow-sm);
  max-width: 22.5rem;
  max-height: 5.5rem;
  margin-bottom: var(--space-xs);
  padding: var(--space-sm);
  transition: transform var(--transition-fast), box-shadow var(--transition-fast);
}

.dashboard__stat-card h3 {
  margin: 0 0 var(--space-xs);
  font-size: var(--font-size-md);
  color: var(--color-text-strong);
}

.dashboard__stat-card p {
  margin: 0;
  line-height: 1.3;
  font-weight: 700;
  font-size: var(--font-size-lg);
  color: var(--color-text);
}

/* ==========================================================================
   Responsive
   ========================================================================== */

@media (max-width: 768px) {
  .dashboard__cards-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .dashboard__cards-grid {
    grid-template-columns: 1fr;
  }
}
</style>
