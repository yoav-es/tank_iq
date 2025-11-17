<template>
  <section class="stats">
    <!-- Header -->
    <h1>Statistics</h1>

    <!-- Controls -->
    <div class="filters">
      <label>
        Time Range:
        <select v-model="selectedRange">
          <option value="7d">Last 7 days</option>
          <option value="30d">Last 30 days</option>
          <option value="90d">Last 90 days</option>
          <option value="all">All time</option>
        </select>
      </label>
      <label>
        Metric:
        <select v-model="selectedMetric">
          <option value="fuel">Fuel</option>
          <option value="distance">Distance</option>
          <option value="cost">Cost</option>
          <option value="efficiency">Efficiency</option>
        </select>
      </label>
    </div>

    <!-- Section: Trend Analysis -->
    <div class="section trend">
      <h2>{{ selectedMetricLabel }} Trend</h2>
      <div class="chart-placeholder">[Line Chart]</div>
    </div>

    <!-- Section: Comparative Analysis -->
    <div class="section comparison">
      <h2>Monthly Comparison</h2>
      <div class="chart-placeholder">[Bar Chart]</div>
    </div>

    <!-- Section: Summary Metrics -->
    <div class="metrics-grid">
      <div class="metric-card">
        <h3>Best</h3>
        <p>{{ bestValue }}</p>
      </div>
      <div class="metric-card">
        <h3>Worst</h3>
        <p>{{ worstValue }}</p>
      </div>
      <div class="metric-card">
        <h3>Average</h3>
        <p>{{ averageValue }}</p>
      </div>
    </div>

    <!-- Section: Detailed Records -->
    <div class="section table">
      <h2>Detailed Records</h2>
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Distance</th>
            <th>Fuel</th>
            <th>Cost</th>
            <th>Efficiency</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="trip in trips" :key="trip.id">
            <td>{{ trip.date }}</td>
            <td>{{ trip.distance }}</td>
            <td>{{ trip.fuel }}</td>
            <td>{{ trip.cost }}</td>
            <td>{{ trip.efficiency }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';

const selectedRange = ref('7d');
const selectedMetric = ref('fuel');

const trips = ref([
  { id: 1, date: '2025-11-01', distance: 45, fuel: 3.2, cost: 4.6, efficiency: 7.1 },
  { id: 2, date: '2025-11-02', distance: 60, fuel: 4.0, cost: 5.8, efficiency: 6.6 },
]);

const selectedMetricLabel = computed(() => {
  switch (selectedMetric.value) {
    case 'fuel': return 'Fuel Consumption';
    case 'distance': return 'Distance';
    case 'cost': return 'Cost';
    case 'efficiency': return 'Efficiency';
    default: return 'Metric';
  }
});

const bestValue = computed(() => Math.min(...trips.value.map(t => t[selectedMetric.value])));
const worstValue = computed(() => Math.max(...trips.value.map(t => t[selectedMetric.value])));
const averageValue = computed(() => {
  const arr = trips.value.map(t => t[selectedMetric.value]);
  return (arr.reduce((a, b) => a + b, 0) / arr.length).toFixed(2);
});
</script>

<style scoped>
.stats {
  display: flex;
  flex-direction: column;
  gap: var(--space-2xl);
}

.filters {
  display: flex;
  gap: var(--space-md);
}

.section {
  background: var(--color-card);
  padding: var(--space-lg);
  border-radius: var(--radius-md);
}

.chart-placeholder {
  height: 220px;
  background: var(--color-chart-bg);
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-muted);
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-md);
}

.metric-card {
  background: var(--color-card);
  padding: var(--space-md);
  border-radius: var(--radius-md);
  text-align: center;
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

/* zebra striping for detailed records */
.section.table tbody tr:nth-child(odd) {
  background-color: var(--color-row-light);
  color: var(--color-text-light);
}

.section.table tbody tr:nth-child(even) {
  background-color: var(--color-row-dark);
  color: var(--color-text-light);
}

.section.table tbody tr:hover {
  background-color: var(--color-row-hover);
}
</style>