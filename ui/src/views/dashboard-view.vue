<!-- ui/src/views/dashboard-view.vue -->
<!-- ui/src/views/dashboard.vue -->
<template>
  <section class="dashboard">
    <h1 class="dashboard__title">📊 Dashboard</h1>

    <!-- Toggle Buttons -->
    <div class="dashboard__toggle-buttons">
      <button
        class="dashboard__toggle-btn"
        :class="{ 'dashboard__toggle-btn--active': viewMode === 'month' }"
        @click="viewMode = 'month'"
      >
        Monthly
      </button>
      <button
        class="dashboard__toggle-btn"
        :class="{ 'dashboard__toggle-btn--active': viewMode === 'year' }"
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
import { ref, shallowRef, markRaw, toRaw, onMounted, onUnmounted, watch, nextTick } from 'vue';
import { Chart, registerables } from 'chart.js';
import type { ChartOptions, ChartData } from 'chart.js';
import { useFuelStore } from '../stores/fuel-store';

Chart.register(...registerables);

type Mode = 'month' | 'year';

const fuelStore = useFuelStore();
const chartRef = ref<HTMLCanvasElement | null>(null);
const chartInstance = shallowRef<Chart<'line'> | null>(null);
const viewMode = ref<Mode>('month');

let isMounted = false;

onMounted(async () => {
  isMounted = true;
  await fuelStore.fetchEntriesAndStats();
  await fuelStore.fetchDetailedStats();
  await nextTick();
  initChart();
});

onUnmounted(() => {
  isMounted = false;
  const chart = chartInstance.value;
  if (chart) {
    chart.stop();
    chart.destroy();
    chartInstance.value = null;
  }
});

watch(viewMode, async () => {
  if (!isMounted) return;
  await nextTick();
  updateChart();
});

function getStats(mode: Mode) {
  const dsRaw = toRaw(fuelStore.detailedStats) as any | null;
  const list: any[] =
    mode === 'month'
      ? [...(dsRaw?.monthly_stats ?? [])]
      : [...(dsRaw?.yearly_stats ?? [])];
  list.sort((a, b) => String(a.period_label).localeCompare(String(b.period_label)));
  return list;
}

function getLabels(mode: Mode, stats: any[]): string[] {
  return stats.map((s) =>
    mode === 'month'
      ? `${String(s.period_label).split('-')[1]}/${String(s.period_label).split('-')[0]}`
      : String(s.period_label)
  );
}

function getData(stats: any[]): number[] {
  return stats.map((s) => Number(s.average_km_per_liter ?? 0));
}

function buildOptions(mode: Mode): ChartOptions<'line'> {
  return {
    responsive: true,
    maintainAspectRatio: false,
    layout: { padding: { bottom: 10 } },
    animation: { duration: 300 },
    plugins: { legend: { display: false } },
    scales: {
      x: {
        title: {
          display: true,
          text: mode === 'month' ? 'Month' : 'Year',
          color: '#f1f5f9',
        },
        ticks: { color: '#f1f5f9' },
      },
      y: {
        title: {
          display: true,
          text: 'Efficiency (km/L)',
          color: '#f1f5f9',
        },
        ticks: { color: '#f1f5f9' },
      },
    },
  };
}

function initChart(): void {
  if (!isMounted || !chartRef.value) return;
  const ctx = chartRef.value.getContext('2d');
  if (!ctx) return;

  const stats = getStats(viewMode.value);
  const labels = getLabels(viewMode.value, stats);
  const dataset = getData(stats);

  const data: ChartData<'line'> = {
    labels,
    datasets: [
      {
        label: `Average Efficiency (${viewMode.value}) [km/L]`,
        data: dataset,
        borderColor: '#10b981',
        backgroundColor: 'rgba(16,185,129,0.2)',
        fill: true,
        tension: 0.3,
      },
    ],
  };

  chartInstance.value = markRaw(
    new Chart<'line'>(ctx, {
      type: 'line',
      data,
      options: buildOptions(viewMode.value),
    })
  );
}

function updateChart(): void {
  const chart = chartInstance.value;
  if (!chart) {
    initChart();
    return;
  }

  const stats = getStats(viewMode.value);
  chart.data.labels = getLabels(viewMode.value, stats);
  chart.data.datasets[0].label = `Average Efficiency (${viewMode.value}) [km/L]`;
  chart.data.datasets[0].data = getData(stats);
  chart.options = buildOptions(viewMode.value);
  chart.update();
}
</script>

<style scoped>
/* ==========================================================================
   Dashboard page
   ========================================================================== */

.page-title {
  font-size: var(--font-size-xl);
  font-weight: 600;
  border-bottom: 2px solid var(--color-accent);
  padding-bottom: var(--space-xs);
}

/* Dashboard layout */
.dashboard {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

/* Toggle buttons */
.dashboard__toggle {
  display: flex;
  gap: var(--space-xs);
}

.dashboard__toggle-button {
  /* baseline button styles come from global .button */
  padding: var(--space-xs) var(--space-md);
  border: 1px solid var(--color-accent);
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  color: var(--color-text);
  cursor: pointer;
  font-weight: 600;
  transition: background-color var(--transition-fast), color var(--transition-fast);
}

.dashboard__toggle-button--active {
  background: var(--color-accent);
  color: var(--color-surface-strong, #fff);
}

/* Graph card */
.dashboard__graph-card {
  background: var(--color-card);
  padding: var(--space-md);
  border-radius: var(--radius-lg);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  height: 440px;
  min-height: 440px;
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
  background: var(--color-highlight, #f9e65c); /* fallback if not defined */
  border-radius: var(--radius-md);
  padding: var(--space-sm);
  text-align: center;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.dashboard__stat-card-title {
  color: var(--color-text-strong, #333);
  margin-bottom: var(--space-xs);
  font-size: var(--font-size-md);
}

.dashboard__stat-card-value {
  font-size: 1rem;
  font-weight: 700;
  color: var(--color-text-strong, #000);
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