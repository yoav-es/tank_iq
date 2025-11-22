<!-- ui/src/views/dashboard-view.vue -->
<template>
  <section class="dashboard">
    <h1 class="page-title">📊 Dashboard</h1>

    <!-- Toggle Buttons -->
    <div class="toggle-buttons">
      <button
        :class="{ active: viewMode === 'month' }"
        @click="viewMode = 'month'"
      >
        Monthly
      </button>
      <button
        :class="{ active: viewMode === 'year' }"
        @click="viewMode = 'year'"
      >
        Yearly
      </button>
    </div>

    <!-- Graph Section -->
    <div class="card graph-card">
      <h3>Average Fuel Efficiency (km/L)</h3>
      <canvas ref="chartRef"></canvas>
    </div>

    <!-- Stats Grid -->
    <div class="cards-grid">
      <div class="card stat-card">
        <h3>Current Avg</h3>
        <p>{{ fuelStore.overallStats?.average_km_per_liter?.toFixed(2) ?? '—' }} km/L</p>
      </div>

      <div class="card stat-card">
        <h3>Best {{ viewMode === 'month' ? 'Month' : 'Year' }}</h3>
        <p>
          {{
            viewMode === 'month'
              ? fuelStore.detailedStats?.overall_stats.best_month_efficiency?.toFixed(2) ?? '—'
              : fuelStore.detailedStats?.overall_stats.best_year_efficiency?.toFixed(2) ?? '—'
          }} km/L
        </p>
      </div>

      <div class="card stat-card">
        <h3>Total Distance</h3>
        <p>{{ fuelStore.overallStats?.total_distance?.toFixed(1) ?? '—' }} km</p>
      </div>

      <div class="card stat-card">
        <h3>Total Cost</h3>
        <p>{{ fuelStore.overallStats?.total_cost?.toFixed(2) ?? '—' }} ₪</p>
      </div>

      <div class="card stat-card">
        <h3>Trips Logged</h3>
        <p>{{ fuelStore.overallStats?.entry_count ?? '—' }}</p>
      </div>

      <div class="card stat-card">
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
.page-title {
  font-size: 2rem;
  font-weight: bold;
  border-bottom: 2px solid var(--color-accent);
  padding-bottom: var(--space-xs);
}

.dashboard {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.toggle-buttons {
  display: flex;
  gap: var(--space-xs);
}
.toggle-buttons button {
  padding: var(--space-xs) var(--space-md);
  border: 1px solid var(--color-accent);
  border-radius: 6px;
  background: var(--color-surface);
  color: var(--color-text);
  cursor: pointer;
  font-weight: bold;
}
.toggle-buttons button.active {
  background: var(--color-accent);
  color: #fff;
}

.graph-card {
  background: var(--color-card);
  padding: var(--space-md);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  height: 440px;
  min-height: 440px;
  overflow: hidden;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-sm);
}
.stat-card {
  background: #f9e65c;
  border-radius: 10px;
  padding: var(--space-sm);
  text-align: center;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}
.stat-card h3 {
  color: #333;
  margin-bottom: var(--space-xs);
  font-size: 0.9rem;
}
.stat-card p {
  font-size: 1rem;
  font-weight: bold;
  color: #000;
}

@media (max-width: 768px) {
  .cards-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 480px) {
  .cards-grid { grid-template-columns: 1fr; }
}
</style>