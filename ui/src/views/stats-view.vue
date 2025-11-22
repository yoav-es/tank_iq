<!-- ui/src/views/stats-view.vue -->
<template>
  <div class="report-container">
    <!-- Header -->
    <header class="report-header">
      <h1>Fuel Efficiency Report</h1>
      <p>Period: 2022 – 2025</p>
    </header>

    <hr class="report-separator" />

    <!-- Executive Summary -->
    <section v-if="summary" class="report-summary">
      <h2>Executive Summary</h2>
      <ul>
        <li>Average yearly efficiency: {{ summary.averageEfficiency }} km/L</li>
        <li>Best year: {{ summary.bestYear }}</li>
        <li>Total fuel cost: {{ summary.totalCost }}</li>
        <li>Total distance: {{ summary.totalDistance }} km</li>
      </ul>
    </section>

    <hr class="report-separator" />

    <!-- Key Insights -->
    <section v-if="thresholdInsights.length" class="report-section">
      <h2>Key Insights</h2>
      <ul class="report-list">
        <li v-for="i in thresholdInsights" :key="i">{{ i }}</li>
      </ul>
    </section>


    <hr class="report-separator" />

    <!-- Yearly Trends -->
    <!-- Yearly Fuel Efficiency Trends -->
    <section v-if="detailedStats" class="report-section">
      <h2>Yearly Fuel Efficiency Trends</h2>
      <div class="chart-wrap">
        <canvas ref="yearlyEfficiencyCanvas"></canvas>
      </div>
    </section>

    <!-- Yearly Fuel Cost Trends -->
    <section v-if="detailedStats" class="report-section">
      <h2>Yearly Fuel Cost Trends</h2>
      <div class="chart-wrap">
        <canvas ref="yearlyCostCanvas"></canvas>
      </div>
    </section>

    <!-- Yearly Summary Table -->
    <section v-if="detailedStats" class="report-section">
      <h2>Yearly Summary Table</h2>
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
          <tr v-for="y in detailedStats.yearly_stats" :key="y.period_label">
            <td>{{ y.period_label }}</td>
            <td>{{ y.average_km_per_liter }}</td>
            <td>{{ y.total_distance }}</td>
            <td>{{ currency(y.total_cost) }}</td>
          </tr>
        </tbody>
      </table>
    </section>
    
    <!-- Yearly Insights -->
    <section v-if="yearlyInsights.length" class="report-section">
      <h2>Yearly Insights</h2>
      <ul class="report-list">
        <li v-for="i in yearlyInsights" :key="i">{{ i }}</li>
      </ul>
    </section>


    
    <hr class="report-separator" />


    <!-- Monthly Trends -->
    <!-- Monthly Fuel Efficiency Trends -->
    <section v-if="detailedStats" class="report-section">
      <h2>Monthly Fuel Efficiency Trends</h2>
      <div class="chart-wrap">
        <canvas ref="monthlyEfficiencyCanvas"></canvas>
      </div>
    </section>

    <!-- Monthly Fuel Cost Trends -->
    <section v-if="detailedStats" class="report-section">
      <h2>Monthly Fuel Cost Trends</h2>
      <div class="chart-wrap">
        <canvas ref="monthlyCostCanvas"></canvas>
      </div>
    </section>

    <!-- Monthly Summary Table -->
    <section v-if="detailedStats" class="report-section">
      <h2>Monthly Summary Table</h2>
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
          <tr v-for="m in detailedStats.monthly_stats" :key="m.period_label">
            <td>{{ m.period_label }}</td>
            <td>{{ m.average_km_per_liter }}</td>
            <td>{{ currency(m.total_cost) }}</td>
            <td>{{ currency(m.average_cost_per_liter) }}</td>
          </tr>
        </tbody>
      </table>
    </section>
    <!-- NEW: Monthly Insights -->
    <section v-if="monthlyInsights.length" class="report-section">
      <h2>Monthly Insights</h2>
      <ul class="report-list">
        <li v-for="i in monthlyInsights" :key="i">{{ i }}</li>
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

// ✅ Store is now used inside <script setup>, safe with Pinia
const store = useFuelStore();
const detailedStats = computed<DetailedStats | null>(() => store.detailedStats ?? null);

const currency = (n: number): string =>
  Intl.NumberFormat(undefined, { style: 'currency', currency: 'USD' }).format(n);

const summary = computed(() => {
  const ds = detailedStats.value;
  if (!ds || ds.yearly_stats.length === 0) return null;

  const avgEfficiency =
    ds.yearly_stats.reduce((sum, y) => sum + y.average_km_per_liter, 0) /
    ds.yearly_stats.length;

  const bestYear = ds.yearly_stats.reduce((best, y) =>
    y.average_km_per_liter > best.average_km_per_liter ? y : best
  );

  const totalCost = ds.monthly_stats.reduce((sum, m) => sum + m.total_cost, 0);
  const totalDistance = ds.yearly_stats.reduce((sum, y) => sum + y.total_distance, 0);

  return {
    averageEfficiency: avgEfficiency.toFixed(2),
    bestYear: bestYear.period_label,
    totalCost: currency(totalCost),
    totalDistance: totalDistance.toFixed(0),
  };
});

const yearlyInsights = computed<string[]>(() => {
  const ds = detailedStats.value;
  if (!ds) return [];

  return ds.yearly_stats.map(y => {
    const notes: string[] = [];
    if (y.average_km_per_liter < 12) {
      notes.push(`${y.period_label}: Efficiency below 12 km/L`);
    }
    if (y.total_cost > 2000) {
      notes.push(`${y.period_label}: High fuel cost (${currency(y.total_cost)})`);
    }
    return notes.join(' | ');
  }).filter(Boolean);
});

const monthlyInsights = computed<string[]>(() => {
  const ds = detailedStats.value;
  if (!ds) return [];

  return ds.monthly_stats.map(m => {
    const notes: string[] = [];
    if (m.average_km_per_liter < 10) {
      notes.push(`${m.period_label}: Efficiency dropped below 10 km/L`);
    }
    if (m.total_cost > 300) {
      notes.push(`${m.period_label}: Spending unusually high (${currency(m.total_cost)})`);
    }
    return notes.join(' | ');
  }).filter(Boolean);
});

const thresholdInsights = computed<string[]>(() => {
  const insights: string[] = [];
  const ds = detailedStats.value;
  if (!ds) return insights;

  const months = ds.monthly_stats ?? [];
  const years = ds.yearly_stats ?? [];

  if (ds.overall_stats.average_km_per_liter < 12) {
    insights.push('Overall efficiency is below 12 km/L — consider maintenance or driving style.');
  }

  if (months.length >= 3) {
    const avgMonthlyCost = months.reduce((s, m) => s + m.total_cost, 0) / months.length;
    const last = months[months.length - 1];
    if (last.total_cost > avgMonthlyCost * 1.2) {
      insights.push(`Last month spending (${currency(last.total_cost)}) is >20% above average (${currency(avgMonthlyCost)}).`);
    }
  }

  if (years.length >= 2) {
    const avgYearDist = years.reduce((s, y) => s + y.total_distance, 0) / years.length;
    const latest = years[years.length - 1];
    if (latest.total_distance > avgYearDist * 1.15) {
      insights.push(`Latest year distance is >15% above multi-year average (${latest.total_distance} km).`);
    }
  }

  return insights;
});



// Canvas refs
const yearlyEfficiencyCanvas = ref<HTMLCanvasElement | null>(null);
const yearlyCostCanvas = ref<HTMLCanvasElement | null>(null);
const monthlyEfficiencyCanvas = ref<HTMLCanvasElement | null>(null);
const monthlyCostCanvas = ref<HTMLCanvasElement | null>(null);

// Chart instances
let yearlyEfficiencyChart: ChartJS | null = null;
let yearlyCostChart: ChartJS | null = null;
let monthlyEfficiencyChart: ChartJS | null = null;
let monthlyCostChart: ChartJS | null = null;

const chartOptions: ChartOptions = {
  responsive: true,
  animation: false,
  maintainAspectRatio: false,
  plugins: {
    legend: { labels: { color: 'var(--color-text)' } }
  },
  scales: {
    x: { ticks: { color: 'var(--color-text)' }, grid: { color: 'var(--color-border)' } },
    y: { ticks: { color: 'var(--color-text)' }, grid: { color: 'var(--color-border)' } }
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

watch(detailedStats, async (ds) => {
  if (!ds) return;
  await nextTick();

  const yearlyLabels = ds.yearly_stats.map(y => y.period_label);
  const yearlyEffData = ds.yearly_stats.map(y => y.average_km_per_liter);
  const yearlyCostData = ds.yearly_stats.map(y => y.total_cost);

  const monthlyLabels = ds.monthly_stats.map(m => m.period_label);
  const monthlyEffData = ds.monthly_stats.map(m => m.average_km_per_liter);
  const monthlyCostData = ds.monthly_stats.map(m => m.total_cost);

  yearlyEfficiencyChart = initOrUpdateChart(
    yearlyEfficiencyChart,
    yearlyEfficiencyCanvas.value,
    'bar',
    yearlyLabels,
    yearlyEffData,
    buildDataset('bar', 'Efficiency (km/L)', yearlyEffData, '#2196F3')
  );

  yearlyCostChart = initOrUpdateChart(
    yearlyCostChart,
    yearlyCostCanvas.value,
    'line',
    yearlyLabels,
    yearlyCostData,
    buildDataset('line', 'Fuel Cost', yearlyCostData, '#FF9800')
  );

  monthlyEfficiencyChart = initOrUpdateChart(
    monthlyEfficiencyChart,
    monthlyEfficiencyCanvas.value,
    'line',
    monthlyLabels,
    monthlyEffData,
    buildDataset('line', 'Efficiency (km/L)', monthlyEffData, '#4CAF50')
  );

  monthlyCostChart = initOrUpdateChart(
    monthlyCostChart,
    monthlyCostCanvas.value,
    'line',
    monthlyLabels,
    monthlyCostData,
    buildDataset('line', 'Fuel Cost', monthlyCostData, '#FF9800')
  );
}, { immediate: true });

onUnmounted(() => {
  yearlyEfficiencyChart?.destroy();
  yearlyCostChart?.destroy();
  monthlyEfficiencyChart?.destroy();
  monthlyCostChart?.destroy();
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
  width: 100%; /* full width like Executive Summary */
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
  padding-left: 0; /* aligned consistently */
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

.report-summary ul {
  border: 1px solid var(--color-border);
  border-radius: 6px;
  list-style: disc;
  padding-left: var(--space-md);
  margin: 0;
}
.report-summary li {
  margin-bottom: var(--space-xs);
  font-size: 1rem;
  color: var(--color-text);
}

.report-insights ul {
  list-style: none;
  padding-left: 0;
  margin: 0;
}
.report-insights li::before {
  content: "•";
  color: var(--color-primary);
  margin-right: 0.5rem;
}
.report-insights li {
  margin-bottom: var(--space-xs);
  color: var(--color-text);
}
.insights-content {
  padding: var(--space-md);
}

/* ===== Charts ===== */
.chart-wrap {
  width: 100%;
  height: 300px;
  margin: var(--space-lg) 0; /* extra breathing room between charts and tables */
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
  margin: var(--space-lg) 0; /* extra spacing above/below tables */
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