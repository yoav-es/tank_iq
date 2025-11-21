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
        <h3>Best {{ viewMode === 'month' ? 'Month' : 'Year' }}</h3>
        <p>
          {{
            viewMode === 'month'
              ? fuelStore.detailedStats?.overall_stats.best_month_efficiency ?? '—'
              : fuelStore.detailedStats?.overall_stats.best_year_efficiency ?? '—'
          }} km/L
      </p>
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
import { ref, onMounted, watch, nextTick, onUnmounted } from 'vue';
import { Chart, registerables } from 'chart.js';
import { useFuelStore } from '../stores/fuel-store';

Chart.register(...registerables);

const fuelStore = useFuelStore();
const chartRef = ref<HTMLCanvasElement | null>(null);
const chartInstance = ref<Chart | null>(null);

// Toggle state
const viewMode = ref<'month' | 'year'>('month');

onMounted(async () => {
  await fuelStore.fetchEntriesAndStats();
  await fuelStore.fetchDetailedStats();
  renderChart();
});

// Re-render chart when toggle changes
watch(viewMode, async () => {
  await nextTick();   // wait for DOM update
  renderChart();
});
onUnmounted(() => {
  if (chartInstance.value) {
    chartInstance.value.destroy();
    chartInstance.value = null;
  }
});

async function renderChart(): Promise<void> {
  if (!chartRef.value || !fuelStore.detailedStats) return;

  const stats =
    viewMode.value === 'month'
      ? (fuelStore.detailedStats?.monthly_stats ?? [])
      : (fuelStore.detailedStats?.yearly_stats ?? []);

  if (!stats.length) return;

  const ctx = chartRef.value.getContext("2d");
  if (!ctx) return;

  if (chartInstance.value) {
    chartInstance.value.destroy();
    chartInstance.value = null;
  }

  chartInstance.value = new Chart(ctx, {
    type: 'line',
    data: {
      labels: stats.map((s) => {
        const [year, month] = s.period_label.split('-');
        return `${month}-${year}`;
      }),
      datasets: [
        {
          label: `Efficiency (${viewMode.value})`,
          data: stats.map((s) => s.average_km_per_liter),
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
      animation: false,
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
  padding-bottom: var(--space-xs);
}

.dashboard {
  display: flex;
  flex-direction: column;
  gap: var(--space-xl);
}

/* Toggle Buttons */
.toggle-buttons {
  display: flex;
  gap: var(--space-md);
  margin-bottom: var(--space-md);
}

.toggle-buttons button {
  padding: var(--space-xs) var(--space-md);
  border: 1px solid var(--color-accent);
  border-radius: 6px;
  background: var(--color-card);
  cursor: pointer;
  font-weight: bold;
}

.toggle-buttons button.active {
  background: var(--color-accent);
  color: #fff;
}

/* Graph Card */
.graph-card {
  background: var(--color-card);
  padding: var(--space-lg);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  height: 400px;
}

/* Stats Grid */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(2, auto);
  gap: var(--space-md);
}

.stat-card {
  background: var(--color-card);
  border-radius: 12px;
  padding: var(--space-md);
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
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
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .cards-grid {
    grid-template-columns: 1fr;
  }
}
</style>