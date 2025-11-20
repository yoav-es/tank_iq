<template>
  <section class="dashboard">
    <h1 class="page-title">📊 Dashboard</h1>

    <!-- Graph Section -->
    <div class="card graph-card">
      <h2>Average Fuel Consumption</h2>
      <canvas ref="chartRef"></canvas>
    </div>

    <!-- Stats Grid -->
    <div class="cards-grid">
      <div class="card stat-card">
        <h3>Current Avg</h3>
        <p>{{ fuelStore.overallStats?.average_km_per_liter ?? '—' }} km/L</p>
      </div>
      <div class="card stat-card">
        <h3>Best Month</h3>
        <p>{{ fuelStore.overallStats?.best_month_efficiency ?? '—' }} km/L</p>
      </div>
      <div class="card stat-card">
        <h3>Total Distance</h3>
        <p>{{ fuelStore.overallStats?.total_distance ?? '—' }} km</p>
      </div>
      <div class="card stat-card">
        <h3>Total Cost</h3>
        <p>${{ fuelStore.overallStats?.total_cost ?? '—' }}</p>
      </div>
      <div class="card stat-card">
        <h3>Trips Logged</h3>
        <p>{{ fuelStore.overallStats?.entry_count ?? '—' }}</p>
      </div>
      <div class="card stat-card">
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

function renderChart(): void {
  if (!chartRef.value || !fuelStore.detailedStats) return;

  if (chartInstance.value) chartInstance.value.destroy();

  chartInstance.value = new Chart(chartRef.value, {
    type: 'line',
    data: {
      labels: fuelStore.detailedStats.monthly_stats.map((s) => s.period_label),
      datasets: [
        {
          label: 'Efficiency (km/L)',
          data: fuelStore.detailedStats.monthly_stats.map((s) => s.average_km_per_liter),
          borderColor: '#4A90E2',
          backgroundColor: 'rgba(74,144,226,0.2)',
          fill: true,
          tension: 0.3,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: true, position: 'bottom' },
      },
    },
  });
}
</script>

<style scoped>
.page-title {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: var(--space-sm); 
  border-bottom: 2px solid var(--color-accent);
  padding-bottom: var(--space-xs); /* reduce padding under the underline */
}


.dashboard {
  display: flex;
  flex-direction: column;
  gap: var(--space-xl);
}

/* Graph Card */
.graph-card {
  background: var(--color-card);
  padding: var(--space-lg);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  height: 400px;
}

/* Stats Grid */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr); /* 3 columns */
  grid-template-rows: repeat(2, auto);   /* 2 rows */
  gap: var(--space-md);
}


.stat-card {
  background: var(--color-card);
  border-radius: 12px;
  padding: var(--space-md);
  text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.stat-card h3 {
  color: var(--color-secondary);
  margin-bottom: var(--space-sm);
  font-size: 1rem;
}

.stat-card p {
  font-size: 1.2rem;
  font-weight: bold;
  color: var(--color-primary);
}

@media (max-width: 768px) {
  .cards-grid {
    grid-template-columns: repeat(2, 1fr); /* 2 columns on tablets */
  }
}

@media (max-width: 480px) {
  .cards-grid {
    grid-template-columns: 1fr; /* single column on phones */
  }
} 
</style>

