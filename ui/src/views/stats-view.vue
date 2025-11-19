<!-- ui/src/views/stats-view.vue -->
<template>
  <section class="stats">
    <h1>Statistics</h1>

    <!-- Controls -->
    <div class="filters">
      <label>
        Time Range:
        <select v-model="selectedRange" @change="fetchStats">
          <option value="7d">Last 7 days</option>
          <option value="30d">Last 30 days</option>
          <option value="90d">Last 90 days</option>
          <option value="all">All time</option>
        </select>
      </label>
      <label>
        Metric:
        <select v-model="selectedMetric" @change="renderTrendChart">
          <option value="fuel">Fuel</option>
          <option value="distance">Distance</option>
          <option value="cost">Cost</option>
          <option value="efficiency">Efficiency</option>
        </select>
      </label>
    </div>

    <!-- Trend Analysis -->
    <div class="section trend">
      <h2>{{ selectedMetricLabel }} Trend</h2>
      <div v-if="!fuelStore.detailedStats?.monthly_stats.length" class="placeholder">
        <p>No statistics available for this range.</p>
      </div>
      <canvas v-else ref="trendChart"></canvas>
    </div>

    <!-- Comparative Analysis -->
    <div class="section comparison">
      <h2>Monthly Comparison</h2>
      <div v-if="!fuelStore.detailedStats?.monthly_stats.length" class="placeholder">
        <p>No statistics available for comparison.</p>
      </div>
      <canvas v-else ref="comparisonChart"></canvas>
    </div>

    <!-- Detailed Records -->
    <div class="section table">
      <h2>Detailed Records</h2>
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Distance</th>
            <th>Fuel</th>
            <th>Cost</th>
            <th>Efficiency (km/L)</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="entry in fuelStore.entries" :key="entry.id">
            <td>{{ entry.date }}</td>
            <td>{{ entry.distance }}</td>
            <td>{{ entry.liters }}</td>
            <td>{{ entry.total_cost }}</td>
            <td>{{ entry.km_per_liter }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { Chart, registerables } from 'chart.js';
import { useFuelStore } from '../stores/fuel-store';

Chart.register(...registerables);

const fuelStore = useFuelStore();

const selectedRange = ref('7d');
const selectedMetric = ref<'fuel' | 'distance' | 'cost' | 'efficiency'>('fuel');

const trendChart = ref<HTMLCanvasElement | null>(null);
const comparisonChart = ref<HTMLCanvasElement | null>(null);
const trendInstance = ref<Chart | null>(null);
const comparisonInstance = ref<Chart | null>(null);

onMounted(async () => {
  await fuelStore.fetchEntriesAndStats();
  await fuelStore.fetchDetailedStats();
  renderTrendChart();
  renderComparisonChart();
});

const selectedMetricLabel = computed(() => {
  switch (selectedMetric.value) {
    case 'fuel': return 'Fuel Consumption';
    case 'distance': return 'Distance';
    case 'cost': return 'Cost';
    case 'efficiency': return 'Efficiency';
    default: return 'Metric';
  }
});

function renderTrendChart() {
  if (!fuelStore.detailedStats?.monthly_stats.length || !trendChart.value) return;

  if (trendInstance.value) trendInstance.value.destroy();

  const stats = fuelStore.detailedStats.monthly_stats;
  const dataPoints = stats.map((s) => {
    switch (selectedMetric.value) {
      case 'fuel': return s.total_liters;
      case 'distance': return s.total_distance;
      case 'cost': return s.total_cost;
      case 'efficiency': return s.average_km_per_liter;
      default: return 0;
    }
  });

  trendInstance.value = new Chart(trendChart.value, {
    type: 'line',
    data: {
      labels: stats.map((s) => s.period_label),
      datasets: [{
        label: selectedMetricLabel.value,
        data: dataPoints,
        borderColor: 'blue',
        fill: false,
      }],
    },
    options: { responsive: true, maintainAspectRatio: false },
  });
}

function renderComparisonChart() {
  if (!fuelStore.detailedStats?.monthly_stats.length || !comparisonChart.value) return;

  if (comparisonInstance.value) comparisonInstance.value.destroy();

  const stats = fuelStore.detailedStats.monthly_stats;

  comparisonInstance.value = new Chart(comparisonChart.value, {
    type: 'bar',
    data: {
      labels: stats.map((s) => s.period_label),
      datasets: [{
        label: 'Efficiency (km/L)',
        data: stats.map((s) => s.average_km_per_liter),
        backgroundColor: 'green',
      }],
    },
    options: { responsive: true, maintainAspectRatio: false },
  });
}

async function fetchStats() {
  await fuelStore.fetchDetailedStats();
  renderTrendChart();
  renderComparisonChart();
}
</script>

<style scoped>
.filters {
  display: flex;
  gap: var(--space-lg);
  margin-bottom: var(--space-lg);
}

.section {
  margin-bottom: var(--space-xl);
}

.section.trend,
.section.comparison {
  height: 350px; /* fixes infinite stretch */
  position: relative;
}

canvas {
  width: 100%;
  height: 100%;
  display: block;
}

.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--color-secondary);
  font-style: italic;
}

.section.table table {
  width: 100%;
  border-collapse: collapse;
}

.section.table th,
.section.table td {
  padding: var(--space-sm);
  border-bottom: 1px solid var(--color-border);
}

.section.table tbody tr:nth-child(odd) {
  background-color: var(--color-row-light);
}

.section.table tbody tr:nth-child(even) {
  background-color: var(--color-row-dark);
}

.section.table tbody tr:hover {
  background-color: var(--color-row-hover);
}
</style>