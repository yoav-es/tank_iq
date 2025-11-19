<!-- ui/src/views/dashboard-view.vue -->
<template>
  <section class="dashboard">
    <h1>Dashboard</h1>

    <!-- Graph Section -->
    <div class="graph-container">
      <h2>Average Fuel Consumption</h2>
      <canvas ref="chartRef"></canvas>
    </div>

    <!-- Cards Grid -->
    <div class="cards-grid">
      <div class="card">
        <h3>Current Avg</h3>
        <p>{{ fuelStore.overallStats?.average_km_per_liter ?? '—' }} km/L</p>
      </div>
      <div class="card">
        <h3>Total Distance</h3>
        <p>{{ fuelStore.overallStats?.total_distance ?? '—' }} km</p>
      </div>
      <div class="card">
        <h3>Total Cost</h3>
        <p>${{ fuelStore.overallStats?.total_cost ?? '—' }}</p>
      </div>
      <div class="card">
        <h3>Trips Logged</h3>
        <p>{{ fuelStore.overallStats?.entry_count ?? '—' }}</p>
      </div>
      <div class="card">
        <h3>Avg Cost/L</h3>
        <p>${{ fuelStore.overallStats?.average_cost_per_liter ?? '—' }}/L</p>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { Chart, registerables } from 'chart.js';
import { useFuelStore } from '../stores/fuel-store';

Chart.register(...registerables);

const fuelStore = useFuelStore();
const chartRef = ref<HTMLCanvasElement | null>(null);
const chartInstance = ref<Chart | null>(null);

onMounted(async () => {
  await fuelStore.fetchEntriesAndStats();
  await fuelStore.fetchDetailedStats();
  renderChart();
});

function renderChart() {
  if (!chartRef.value || !fuelStore.detailedStats) return;

  // Destroy old chart before creating a new one
  if (chartInstance.value) {
    chartInstance.value.destroy();
  }

  chartInstance.value = new Chart(chartRef.value, {
    type: 'line',
    data: {
      labels: fuelStore.detailedStats.monthly_stats.map((stat) => stat.period_label),
      datasets: [
        {
          label: 'Efficiency (km/L)',
          data: fuelStore.detailedStats.monthly_stats.map((stat) => stat.average_km_per_liter),
          borderColor: 'blue',
          fill: false,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
    },
  });
}
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: var(--space-2xl);
}

/* Graph Section */
.graph-container {
  background: var(--color-card);
  padding: var(--space-lg);
  border-radius: 8px;
  height: 350px; /* fixed height for chart container */
}

canvas {
  width: 100%;
  height: 100%; /* chart fills container */
  display: block;
  border-radius: 6px;
}

/* Cards Grid */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-md);
}

.card {
  background: var(--color-card);
  border-radius: 8px;
  padding: var(--space-md);
  text-align: center;
  box-shadow: 0 2px 6px rgba(0,0,0,0.25);
}

.card h3 {
  color: var(--color-secondary);
  margin-bottom: var(--space-sm);
}

/* Responsive */
@media (max-width: 768px) {
  .cards-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (max-width: 480px) {
  .cards-grid {
    grid-template-columns: 1fr;
  }
}
</style>