<!-- ui/src/views/DashboardView.vue -->
<!-- ui/src/views/DashboardView.vue -->
<template>
  <section class="dashboard">
    <!-- Headline -->
    <h1 class="headline headline--compact">📊 Dashboard</h1>

    <!-- Toggle Buttons -->
    <div class="dashboard__toggle-buttons">
      <button
        class="button"
        :class="{ 'button--primary': viewMode === 'month' }"
        @click="viewMode = 'month'"
        :aria-pressed="viewMode === 'month'"
      >
        Monthly
      </button>

      <button
        class="button"
        :class="{ 'button--primary': viewMode === 'year' }"
        @click="viewMode = 'year'"
        :aria-pressed="viewMode === 'year'"
      >
        Yearly
      </button>
    </div>

    <!-- Graph Section -->
    <div class="panel dashboard__graph-card">
      <h3 class="dashboard__graph-title">Average Fuel Efficiency (km/L)</h3>
      <template v-if="hasStats(fuelStore.detailedStats, viewMode)">
        <canvas ref="chartRef" aria-label="Fuel efficiency chart"></canvas>
      </template>
      <template v-else>
        <p>No data available to display chart.</p>
      </template>
    </div>

    <!-- Stats Grid -->
    <div class="dashboard__cards-grid">
      <div class="panel dashboard__stat-card">
        <h3>Current Avg</h3>
        <p>{{ fuelStore.overallStats?.average_km_per_liter?.toFixed(2) ?? '—' }} km/L</p>
      </div>

      <div class="panel dashboard__stat-card">
        <h3>Best {{ viewMode === 'month' ? 'Month' : 'Year' }}</h3>
        <p>
          {{
            viewMode === 'month'
              ? fuelStore.detailedStats?.overall_stats.best_month_efficiency?.toFixed(2) ?? '—'
              : fuelStore.detailedStats?.overall_stats.best_year_efficiency?.toFixed(2) ?? '—'
          }} km/L
        </p>
      </div>

      <div class="panel dashboard__stat-card">
        <h3>Total Distance</h3>
        <p>{{ fuelStore.overallStats?.total_distance?.toFixed(1) ?? '—' }} km</p>
      </div>

      <div class="panel dashboard__stat-card">
        <h3>Total Cost</h3>
        <p>{{ fuelStore.overallStats?.total_cost?.toFixed(2) ?? '—' }} ₪</p>
      </div>

      <div class="panel dashboard__stat-card">
        <h3>Trips Logged</h3>
        <p>{{ fuelStore.overallStats?.entry_count ?? '—' }}</p>
      </div>

      <div class="panel dashboard__stat-card">
        <h3>Avg Cost/L</h3>
        <p>{{ fuelStore.overallStats?.average_cost_per_liter?.toFixed(2) ?? '—' }} ₪/L</p>
      </div>
    </div>
  </section>
</template>


<script setup lang="ts">
import { ref, shallowRef, onMounted, onUnmounted, watch, nextTick } from 'vue';
import type { Chart } from 'chart.js';
import { useFuelStore } from '../stores/fuelStore';
import {
  Mode,
  getStats,
  hasStats,
  getLabels,
  getData,
  initOrUpdateChart,
  buildDataset,
  buildOptions
} from '../composables/useChart';

/**
 * Fuel store instance for accessing entries and stats.
 */
const fuelStore = useFuelStore();

/**
 * Reference to the chart canvas element.
 */
const chartRef = ref<HTMLCanvasElement | null>(null);

/**
 * Chart.js instance for the dashboard chart.
 */
const chartInstance = shallowRef<Chart<'line'> | null>(null);

/**
 * Current view mode for stats (month/year).
 */
const viewMode = ref<Mode>('month');

/**
 * Initialize chart when component mounts.
 */
onMounted(async () => {
  try {
    await fuelStore.fetchEntriesAndStats();
    await fuelStore.fetchDetailedStats();
    await nextTick();

    if (chartRef.value && hasStats(fuelStore.detailedStats, viewMode.value)) {
      const stats = getStats(fuelStore.detailedStats, viewMode.value);
      const labels = getLabels(viewMode.value, stats);
      const data = getData(stats);
      const dataset = buildDataset('line', data, '#10B981');
      const options = buildOptions(viewMode.value, 'Efficiency (km/L)', 'Average Fuel Efficiency');

      chartInstance.value = initOrUpdateChart(
        chartInstance.value,
        chartRef.value,
        'line',
        labels,
        data,
        dataset,
        options
      ) as Chart<'line'>;
    }
  } catch (err) {
    console.error('Failed to initialize dashboard:', err);
  }
});

/**
 * Cleanup chart when component unmounts.
 */
onUnmounted(() => {
  chartInstance.value?.destroy();
  chartInstance.value = null;
});

/**
 * Watch for mode changes and update chart accordingly.
 */
watch(viewMode, async () => {
  await nextTick();
  if (chartRef.value) {
    if (hasStats(fuelStore.detailedStats, viewMode.value)) {
      const stats = getStats(fuelStore.detailedStats, viewMode.value);
      const labels = getLabels(viewMode.value, stats);
      const data = getData(stats);
      const dataset = buildDataset('line', data, '#10B981');
      const options = buildOptions(viewMode.value, 'Efficiency (km/L)', 'Average Fuel Efficiency');

      chartInstance.value = initOrUpdateChart(
        chartInstance.value,
        chartRef.value,
        'line',
        labels,
        data,
        dataset,
        options
      ) as Chart<'line'>;
    } else {
      chartInstance.value?.destroy();
      chartInstance.value = null;
    }
  }
});
</script>

<style scoped>
/* ==========================================================================
   Dashboard layout
   ========================================================================== */
.dashboard {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

/* Toggle buttons */
.dashboard__toggle-buttons {
  display: flex;
  gap: var(--space-sm);
}

/* Inactive toggle buttons */
.dashboard__toggle-buttons button:not(.button--primary) {
  background: var(--color-surface);
  color: var(--color-text);
}

/* Headline – compact spacing modifier */
.headline--compact {
  padding-bottom: var(--space-xs);
  margin-bottom: var(--space-xs);
}

/* Graph card */
.dashboard__graph-card {
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.dashboard__graph-title {
  margin-bottom: var(--space-sm);
  font-size: var(--font-size-md);
  font-weight: 600;
  color: var(--color-text-strong);
}

.dashboard__graph-card canvas {
  width: 100%;
  height: 100%;
  max-height: 400px; /* prevent runaway growth */
}

/* Cards grid */
.dashboard__cards-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-sm);
}

/* Stat card tweaks */
.dashboard__stat-card {
  text-align: center;
  background: var(--color-card);
  font-weight: 700;
  max-width: 28rem;       /* wider */
  max-height: 5rem;       /* taller */
  margin-bottom: var(--space-xs);
  padding: var(--space-xs); /* more breathing room */
  transition: transform var(--transition-fast), box-shadow var(--transition-fast);
}

.dashboard__stat-card h3 {
  margin: 0 0 var(--space-xs);
  font-size: var(--font-size-lg);   /* larger heading */
  color: var(--color-text-strong);
}

.dashboard__stat-card p {
  margin: 0;
  line-height: 1.4;
  font-weight: 700;
  font-size: var(--font-size-lg);   /* larger value text */
  color: var(--color-text);
}

/* Responsive */
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

