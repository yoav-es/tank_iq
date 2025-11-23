<!-- ui/src/views/stats-view.vue (refactored) -->
<template>
  <div class="report-container">
    <!-- Header -->
    <header class="report-header">
      <h1>Fuel Efficiency Report</h1>
      <p>{{ headerPeriodLabel }}</p>
    </header>

    <hr class="report-separator" />

    <!-- Controls -->
    <section class="report-section">
      <h2>Controls</h2>
      <div style="display:flex; gap:1rem; align-items:center;">
        <label>
          <strong>View:</strong>
          <select v-model="viewMode">
            <option value="yearly">Yearly</option>
            <option value="monthly">Monthly</option>
          </select>
        </label>

        <label v-if="viewMode === 'yearly'">
          <strong>Period:</strong>
          <select v-model="selectedPeriod">
            <option v-for="y in yearlyLabels" :key="y" :value="y">{{ y }}</option>
          </select>
        </label>

        <label v-else>
          <strong>Period:</strong>
          <select v-model="selectedPeriod">
            <option v-for="m in monthlyLabels" :key="m" :value="m">{{ m }}</option>
          </select>
        </label>
      </div>
    </section>

    <hr class="report-separator" />

    <!-- Executive summary -->
    <section v-if="summaryBlock" class="report-summary">
      <h2>Executive Summary</h2>
      <p>
        {{ summaryBlock.periodText }}
        Vehicles traveled a total of {{ summaryBlock.totalDistance }} km, with an overall efficiency of
        {{ summaryBlock.averageEfficiency }} km/L. Total spending reached {{ summaryBlock.totalCost }}.
        Compared to previous periods, efficiency was {{ summaryBlock.efficiencyCompare }},
        and costs {{ summaryBlock.costCompare }}.
      </p>
    </section>

    <hr class="report-separator" />

    <!-- Yearly analysis -->
    <section v-if="viewMode === 'yearly' && detailedStats" class="report-section">
      <h2>Yearly Fuel Efficiency Trends</h2>
      <div class="chart-wrap">
        <canvas ref="yearlyEfficiencyCanvas"></canvas>
      </div>
    </section>

    <section v-if="viewMode === 'yearly' && detailedStats" class="report-section">
      <h2>Yearly Fuel Cost Trends</h2>
      <div class="chart-wrap">
        <canvas ref="yearlyCostCanvas"></canvas>
      </div>
    </section>

    <section v-if="viewMode === 'yearly' && detailedStats" class="report-section">
      <h2>Yearly Distance Trends</h2>
      <div class="chart-wrap">
        <canvas ref="yearlyDistanceCanvas"></canvas>
      </div>
    </section>

    <section v-if="viewMode === 'yearly' && selectedYearRow" class="report-section">
      <h2>Yearly Summary (selected)</h2>
      <table class="report-table">
        <thead>
          <tr>
            <th>Year</th>
            <th>Efficiency (km/L)</th>
            <th>Distance (km)</th>
            <th>Total Cost</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>{{ selectedYearRow.period_label }}</td>
            <td>{{ selectedYearRow.average_km_per_liter }}</td>
            <td>{{ selectedYearRow.total_distance }}</td>
            <td>{{ currency(selectedYearRow.total_cost) }}</td>
          </tr>
        </tbody>
      </table>
    </section>

    <!-- Insights moved to bottom -->
    <section v-if="viewMode === 'yearly' && insightsYearlySelected.length" class="report-section">
      <h2>Insights</h2>
      <ul class="report-list">
        <li v-for="i in insightsYearlySelected" :key="i">{{ i }}</li>
      </ul>
    </section>

    <hr class="report-separator" />

    <!-- Monthly analysis -->
    <section v-if="viewMode === 'monthly' && detailedStats" class="report-section">
      <h2>Monthly Fuel Efficiency Trends</h2>
      <div class="chart-wrap">
        <canvas ref="monthlyEfficiencyCanvas"></canvas>
      </div>
    </section>

    <section v-if="viewMode === 'monthly' && detailedStats" class="report-section">
      <h2>Monthly Fuel Cost Trends</h2>
      <div class="chart-wrap">
        <canvas ref="monthlyCostCanvas"></canvas>
      </div>
    </section>

    <section v-if="viewMode === 'monthly' && detailedStats" class="report-section">
      <h2>Monthly Distance Trends</h2>
      <div class="chart-wrap">
        <canvas ref="monthlyDistanceCanvas"></canvas>
      </div>
    </section>

    <section v-if="viewMode === 'monthly' && selectedMonthRow" class="report-section">
      <h2>Monthly Summary (selected)</h2>
      <table class="report-table">
        <thead>
          <tr>
            <th>Month</th>
            <th>Efficiency (km/L)</th>
            <th>Fuel Cost</th>
            <th>Price/L</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>{{ selectedMonthRow.period_label }}</td>
            <td>{{ selectedMonthRow.average_km_per_liter }}</td>
            <td>{{ currency(selectedMonthRow.total_cost) }}</td>
            <td>{{ currency(selectedMonthRow.average_cost_per_liter) }}</td>
          </tr>
        </tbody>
      </table>
    </section>

    <!-- Insights moved to bottom -->
    <section v-if="viewMode === 'monthly' && insightsMonthlySelected.length" class="report-section">
      <h2>Insights</h2>
      <ul class="report-list">
        <li v-for="i in insightsMonthlySelected" :key="i">{{ i }}</li>
      </ul>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onUnmounted } from 'vue';
import { useFuelStore } from '../stores/fuel-store';
import type { DetailedStats } from '../types/fuel-entry';
import {
  Chart as ChartJS,
  ChartOptions,
  ChartType,
  registerables
} from 'chart.js';

ChartJS.register(...registerables);

// Store
const store = useFuelStore();
const detailedStats = computed<DetailedStats | null>(() => store.detailedStats ?? null);

// View/Period controls
const viewMode = ref<'yearly' | 'monthly'>('yearly');
const selectedPeriod = ref<string>('');

// Currency variable (configurable)
const currencyCode = ref('ILS'); // change as needed
const currency = (n: number): string =>
  Intl.NumberFormat(undefined, { style: 'currency', currency: currencyCode.value }).format(n);

// Labels (old -> new for selectors)
const yearlyLabels = computed(() => {
  const ds = detailedStats.value;
  return ds ? ds.yearly_stats.map(y => y.period_label).reverse() : [];
});
const monthlyLabels = computed(() => {
  const ds = detailedStats.value;
  return ds ? ds.monthly_stats.map(m => m.period_label).reverse() : [];
});

// Initialize selected period when data arrives or view changes
watch([detailedStats, viewMode], () => {
  const ds = detailedStats.value;
  if (!ds) return;
  if (viewMode.value === 'yearly') {
    const labels = yearlyLabels.value;
    if (labels.length && !labels.includes(selectedPeriod.value)) {
      selectedPeriod.value = labels[labels.length - 1]; // default to latest year (rightmost)
    }
  } else {
    const labels = monthlyLabels.value;
    if (labels.length && !labels.includes(selectedPeriod.value)) {
      selectedPeriod.value = labels[labels.length - 1]; // default to latest month (rightmost)
    }
  }
}, { immediate: true });

// Selected rows
const selectedYearRow = computed(() => {
  if (viewMode.value !== 'yearly') return null;
  const ds = detailedStats.value;
  if (!ds) return null;
  return ds.yearly_stats.find(y => y.period_label === selectedPeriod.value) ?? null;
});
const selectedMonthRow = computed(() => {
  if (viewMode.value !== 'monthly') return null;
  const ds = detailedStats.value;
  if (!ds) return null;
  return ds.monthly_stats.find(m => m.period_label === selectedPeriod.value) ?? null;
});

// Header period label
const headerPeriodLabel = computed(() => {
  const ds = detailedStats.value;
  if (!ds) return 'Period: —';
  const firstYear = ds.yearly_stats[0]?.period_label ?? '—';
  const lastYear = ds.yearly_stats[ds.yearly_stats.length - 1]?.period_label ?? '—';
  return `Period: ${firstYear} – ${lastYear}`;
});

// Summary block
const summaryBlock = computed(() => {
  const ds = detailedStats.value;
  if (!ds) return null;

  if (viewMode.value === 'yearly' && selectedYearRow.value) {
    const row = selectedYearRow.value;
    const avgAllYears =
      ds.yearly_stats.reduce((s, y) => s + y.average_km_per_liter, 0) / ds.yearly_stats.length;
    const avgAllCost =
      ds.yearly_stats.reduce((s, y) => s + y.total_cost, 0) / ds.yearly_stats.length;

    return {
      periodText: `This report summarizes fuel efficiency and costs for ${row.period_label}.`,
      totalDistance: row.total_distance.toFixed(0),
      averageEfficiency: row.average_km_per_liter.toFixed(2),
      totalCost: currency(row.total_cost),
      efficiencyCompare: row.average_km_per_liter >= avgAllYears ? 'higher' : 'lower',
      costCompare: row.total_cost >= avgAllCost ? 'rose' : 'fell'
    };
  }

  if (viewMode.value === 'monthly' && selectedMonthRow.value) {
    const row = selectedMonthRow.value;
    const yearKey = row.period_label.slice(0, 4);
    const monthsSameYear = ds.monthly_stats.filter(m => m.period_label.startsWith(yearKey));
    const avgYearEff =
      monthsSameYear.length
        ? monthsSameYear.reduce((s, m) => s + m.average_km_per_liter, 0) / monthsSameYear.length
        : row.average_km_per_liter;
    const avgYearCost =
      monthsSameYear.length
        ? monthsSameYear.reduce((s, m) => s + m.total_cost, 0) / monthsSameYear.length
        : row.total_cost;

    return {
      periodText: `This report summarizes fuel efficiency and costs for ${row.period_label}.`,
      totalDistance: row.total_distance?.toFixed?.(0) ?? '0',
      averageEfficiency: row.average_km_per_liter.toFixed(2),
      totalCost: currency(row.total_cost),
      efficiencyCompare: row.average_km_per_liter >= avgYearEff ? 'higher' : 'lower',
      costCompare: row.total_cost >= avgYearCost ? 'rose' : 'fell'
    };
  }

  return null;
});

// Insights
const insightsYearlySelected = computed<string[]>(() => {
  const row = selectedYearRow.value;
  if (!row) return [];
  const items: string[] = [];
  items.push(`${row.period_label} shows an average efficiency of ${row.average_km_per_liter.toFixed(2)} km/L.`);
  if (row.average_km_per_liter < 12) {
    items.push('Efficiency is below 12 km/L, suggesting maintenance or driving adjustments.');
  }
  items.push(`Total distance was ${row.total_distance.toFixed(0)} km, indicating usage level for the year.`);
  items.push(`Fuel costs reached ${currency(row.total_cost)}, reflecting price trends or higher demand.`);
  return items;
});

const insightsMonthlySelected = computed<string[]>(() => {
  const row = selectedMonthRow.value;
  if (!row) return [];
  const items: string[] = [];
  items.push(`${row.period_label} recorded an average efficiency of ${row.average_km_per_liter.toFixed(2)} km/L.`);
  if (row.average_km_per_liter < 10) {
    items.push('Efficiency dropped below 10 km/L, hinting at mechanical or driving-condition factors.');
  }
  items.push(`Fuel spending totaled ${currency(row.total_cost)} for the month.`);
  if (typeof row.total_distance === 'number') {
    items.push(`Vehicles traveled ${row.total_distance.toFixed(0)} km, consistent with seasonal patterns.`);
  }
  return items;
});

// Chart refs
const yearlyEfficiencyCanvas = ref<HTMLCanvasElement | null>(null);
const yearlyCostCanvas = ref<HTMLCanvasElement | null>(null);
const monthlyEfficiencyCanvas = ref<HTMLCanvasElement | null>(null);
const monthlyCostCanvas = ref<HTMLCanvasElement | null>(null);
const yearlyDistanceCanvas = ref<HTMLCanvasElement | null>(null);
const monthlyDistanceCanvas = ref<HTMLCanvasElement | null>(null);

// Chart instances
let yearlyEfficiencyChart: ChartJS | null = null;
let yearlyCostChart: ChartJS | null = null;
let monthlyEfficiencyChart: ChartJS | null = null;
let monthlyCostChart: ChartJS | null = null;
let yearlyDistanceChart: ChartJS | null = null;
let monthlyDistanceChart: ChartJS | null = null;

// Chart options with axis labels
const chartOptions: ChartOptions = {
  responsive: true,
  animation: false,
  maintainAspectRatio: false,
  plugins: {
    legend: { labels: { color: 'var(--color-text)' } }
  },
  scales: {
    x: {
      title: { display: true, text: 'Period', color: 'var(--color-text)' },
      ticks: { color: 'var(--color-text)' },
      grid: { color: 'var(--color-border)' }
    },
    y: {
      title: { display: true, text: 'Value', color: 'var(--color-text)' },
      ticks: { color: 'var(--color-text)' },
      grid: { color: 'var(--color-border)' }
    }
  }
};

function arraysChanged(a: unknown[], b: unknown[]) {
  if (a.length !== b.length) return true;
  return a.some((val, i) => val !== b[i]);
}

function buildDataset(type: 'bar' | 'line', label: string, data: number[], color: string) {
  if (type === 'bar') {
    return { label, data, backgroundColor: color };
  }
  return { label, data, borderColor: color, tension: 0.3, fill: false };
}

function initOrUpdateChart(
  chart: ChartJS | null,
  canvas: HTMLCanvasElement | null,
  type: ChartType,
  labels: string[],
  data: number[],
  dataset: any
): ChartJS | null {
  if (!chart && canvas) {
    return new ChartJS(canvas, {
      type,
      data: { labels, datasets: [dataset] },
      options: chartOptions
    });
  } else if (chart) {
    const needUpdate =
      arraysChanged(chart.data.labels as string[], labels) ||
      arraysChanged(chart.data.datasets[0].data as number[], data);
    if (needUpdate) {
      chart.data.labels = labels;
      chart.data.datasets[0].data = data;
      chart.update();
    }
  }
  return chart;
}

// Build chart data (always old -> new)
watch([detailedStats, viewMode, selectedPeriod], async ([ds]) => {
  if (!ds) return;
  await nextTick();

  // Yearly charts (old -> new)
  const yearlyLabelsData = ds.yearly_stats.map(y => y.period_label).reverse();
  const yearlyEffData = ds.yearly_stats.map(y => y.average_km_per_liter).reverse();
  const yearlyCostData = ds.yearly_stats.map(y => y.total_cost).reverse();
  const yearlyDistData = ds.yearly_stats.map(y => y.total_distance).reverse();

  yearlyEfficiencyChart = initOrUpdateChart(
    yearlyEfficiencyChart,
    yearlyEfficiencyCanvas.value,
    'bar',
    yearlyLabelsData,
    yearlyEffData,
    buildDataset('bar', 'Efficiency (km/L)', yearlyEffData, '#2196F3')
  );

  yearlyCostChart = initOrUpdateChart(
    yearlyCostChart,
    yearlyCostCanvas.value,
    'line',
    yearlyLabelsData,
    yearlyCostData,
    buildDataset('line', 'Fuel Cost', yearlyCostData, '#FF9800')
  );

  yearlyDistanceChart = initOrUpdateChart(
    yearlyDistanceChart,
    yearlyDistanceCanvas.value,
    'line',
    yearlyLabelsData,
    yearlyDistData,
    buildDataset('line', 'Distance (km)', yearlyDistData, '#9C27B0')
  );

  // Monthly charts (old -> new)
  const monthlyLabelsData = ds.monthly_stats.map(m => m.period_label).reverse();
  const monthlyEffData = ds.monthly_stats.map(m => m.average_km_per_liter).reverse();
  const monthlyCostData = ds.monthly_stats.map(m => m.total_cost).reverse();
  const monthlyDistData = ds.monthly_stats.map(m => m.total_distance).reverse();

  monthlyEfficiencyChart = initOrUpdateChart(
    monthlyEfficiencyChart,
    monthlyEfficiencyCanvas.value,
    'line',
    monthlyLabelsData,
    monthlyEffData,
    buildDataset('line', 'Efficiency (km/L)', monthlyEffData, '#4CAF50')
  );

  monthlyCostChart = initOrUpdateChart(
    monthlyCostChart,
    monthlyCostCanvas.value,
    'line',
    monthlyLabelsData,
    monthlyCostData,
    buildDataset('line', 'Fuel Cost', monthlyCostData, '#FF9800')
  );

  monthlyDistanceChart = initOrUpdateChart(
    monthlyDistanceChart,
    monthlyDistanceCanvas.value,
    'line',
    monthlyLabelsData,
    monthlyDistData,
    buildDataset('line', 'Distance (km)', monthlyDistData, '#9C27B0')
  );
}, { immediate: true });

// Destroy charts on unmount
onUnmounted(() => {
  yearlyEfficiencyChart?.destroy();
  yearlyCostChart?.destroy();
  yearlyDistanceChart?.destroy();
  monthlyEfficiencyChart?.destroy();
  monthlyCostChart?.destroy();
  monthlyDistanceChart?.destroy();
});
</script>

<style scoped>
/* ===== Report Container ===== */
.report-container {
  margin: 0 auto;
  width: 100%;
  max-width: none;
  font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
  color: var(--color-text);
}

/* ===== Header ===== */
.report-header {
  text-align: center;
  margin-bottom: var(--space-lg);
}
.report-header h1 {
  font-size: 2rem;
  font-weight: 700;
  margin: 0;
  color: var(--color-text-strong);
}
.report-header p {
  margin: 0;
  color: var(--color-text);
}

/* ===== Separator ===== */
.report-separator {
  border: none;
  border-top: 2px solid var(--color-border);
  margin: var(--space-lg) 0;
}

/* ===== Section Blocks ===== */
.report-section,
.report-summary,
.report-insights {
  background: var(--color-card);
  border-radius: 12px;
  padding: var(--space-md);
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
  margin-bottom: var(--space-lg);
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

/* ===== Section Headings ===== */
section > h2,
.report-summary h2,
.report-section h2,
.report-insights h2 {
  font-size: 1.4rem;
  font-weight: 600;
  margin-bottom: var(--space-sm);
  color: var(--color-text-strong);
  border-bottom: 2px solid var(--color-accent);
  padding-bottom: var(--space-xs);
  padding-left: 0;
}

/* ===== Lists ===== */
.report-list {
  border: 1px solid var(--color-border);
  border-radius: 6px;
  list-style: disc;
  padding-left: var(--space-md);
  margin: 0;
}
.report-list li {
  margin-bottom: var(--space-xs);
  font-size: 1rem;
  color: var(--color-text);
}

/* ===== Charts ===== */
.chart-wrap {
  width: 100%;
  height: 300px;
  margin: var(--space-lg) 0;
}
.chart-wrap canvas {
  width: 100% !important;
  height: 100% !important;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: var(--color-input-bg);
  padding: var(--space-xs);
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

/* ===== Tables ===== */
.report-table {
  width: 100%;
  border-collapse: collapse;
  margin: var(--space-lg) 0;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  overflow: hidden;
}
.report-table thead th {
  text-align: left;
  font-weight: 600;
  color: var(--color-text-strong);
  background: var(--color-row-light);
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.report-table th,
.report-table td {
  padding: var(--space-xs);
  border-bottom: 1px solid var(--color-border);
  color: var(--color-text);
}
.report-table tbody tr:nth-child(odd) { background-color: var(--color-row-light); }
.report-table tbody tr:nth-child(even) { background-color: var(--color-row-dark); }
.report-table tbody tr:hover {
  background-color: var(--color-row-hover);
  transition: background-color 0.2s ease;
}

/* ===== Print Styles ===== */
@media print {
  .report-container { max-width: none; margin: 0; padding: 0; color: #000; }
  .report-header { text-align: center; margin-bottom: 12pt; }
  .chart-wrap { height: 240px; margin: 12pt 0; }
  .chart-wrap canvas { border: 1pt solid #000; box-shadow: none; }
  .report-table { border: 1pt solid #000; margin: 12pt 0; }
  .report-table thead th, .report-table td { border-bottom: 1pt solid #000; }
  .report-section, .report-summary ul, .report-insights ul { page-break-inside: avoid; }
}
</style>