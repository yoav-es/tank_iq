<!-- ui/src/views/stats-view.vue -->
<template>
  <div class="report-container">
    <header class="report__header">
      <h1 class="report__title">Fuel Efficiency Report</h1>
      <p class="report__subtitle">{{ headerPeriodLabel }}</p>
    </header>

    <hr class="report__separator" />

    <section class="report__block">
      <h2 class="report__heading">Controls</h2>
      <div class="u-flex u-gap-md u-align-start">
        <label>
          <strong>View: </strong>
          <select v-model="viewMode" class="select">
            <option value="yearly">Yearly</option>
            <option value="monthly">Monthly</option>
          </select>
        </label>

        <label v-if="viewMode === 'yearly'">
          <strong>Period: </strong>
          <select v-model="selectedPeriod" class="select">
            <option v-for="y in yearlyLabels" :key="y" :value="y">{{ y }}</option>
          </select>
        </label>

        <label v-else>
          <strong>Period: </strong>
          <select v-model="selectedPeriod" class="select">
            <option v-for="m in monthlyLabels" :key="m" :value="m">{{ m }}</option>
          </select>
        </label>
      </div>
    </section>

    <hr class="report__separator" />

    <section v-if="summaryBlock" class="report__block">
      <h2 class="report__heading">Executive Summary</h2>
      <p>
        {{ summaryBlock.periodText }}
        Vehicles traveled a total of {{ summaryBlock.totalDistance }} km, with an overall efficiency of
        {{ summaryBlock.averageEfficiency }} km/L. Total spending reached {{ summaryBlock.totalCost }}.
        Compared to previous periods, efficiency was {{ summaryBlock.efficiencyCompare }},
        and costs {{ summaryBlock.costCompare }}.
      </p>
    </section>
    <hr v-if="summaryBlock" class="report__separator" />

    <section v-if="viewMode === 'yearly' && detailedStats" class="report__block">
      <h2 class="report__heading">Yearly Fuel Efficiency Trends</h2>
      <div class="report__chart">
        <canvas ref="yearlyEfficiencyCanvas" class="report__chart-canvas"></canvas>
      </div>
    </section>

    <section v-if="viewMode === 'yearly' && detailedStats" class="report__block">
      <h2 class="report__heading">Yearly Fuel Cost Trends</h2>
      <div class="report__chart">
        <canvas ref="yearlyCostCanvas" class="report__chart-canvas"></canvas>
      </div>
    </section>

    <section v-if="viewMode === 'yearly' && detailedStats" class="report__block">
      <h2 class="report__heading">Yearly Distance Trends</h2>
      <div class="report__chart">
        <canvas ref="yearlyDistanceCanvas" class="report__chart-canvas"></canvas>
      </div>
    </section>

    <section v-if="viewMode === 'yearly' && selectedYearRow" class="report__block">
      <h2 class="report__heading">Yearly Summary (selected)</h2>
      <table class="report__table">
        <thead class="report__table-head">
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

    <section v-if="viewMode === 'yearly' && insightsYearlySelected" class="report__block">
      <h2 class="report__heading">Insights</h2>
      <p class="report__insight">{{ insightsYearlySelected }}</p>
    </section>
    <hr v-if="viewMode === 'yearly' && insightsYearlySelected" class="report__separator" />

    <section v-if="viewMode === 'monthly' && detailedStats" class="report__block">
      <h2 class="report__heading">Monthly Fuel Efficiency Trends</h2>
      <div class="report__chart">
        <canvas ref="monthlyEfficiencyCanvas" class="report__chart-canvas"></canvas>
      </div>
    </section>

    <section v-if="viewMode === 'monthly' && detailedStats" class="report__block">
      <h2 class="report__heading">Monthly Fuel Cost Trends</h2>
      <div class="report__chart">
        <canvas ref="monthlyCostCanvas" class="report__chart-canvas"></canvas>
      </div>
    </section>

    <section v-if="viewMode === 'monthly' && detailedStats" class="report__block">
      <h2 class="report__heading">Monthly Distance Trends</h2>
      <div class="report__chart">
        <canvas ref="monthlyDistanceCanvas" class="report__chart-canvas"></canvas>
      </div>
    </section>

    <section v-if="viewMode === 'monthly' && selectedMonthRow" class="report__block">
      <h2 class="report__heading">Monthly Summary (selected)</h2>
      <table class="report__table">
        <thead class="report__table-head">
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

    <section v-if="viewMode === 'monthly' && insightsMonthlySelected" class="report__block">
      <h2 class="report__heading">Insights</h2>
      <p class="report__insight">{{ insightsMonthlySelected }}</p>
    </section>
    <hr v-if="viewMode === 'monthly' && insightsMonthlySelected" class="report__separator" />

    <section v-if="detailedStats" class="report__block">
      <h2 class="report__heading">Fuel Efficiency Distribution</h2>
      <div class="report__chart">
        <canvas ref="efficiencyHistogramCanvas" class="report__chart-canvas"></canvas>
      </div>
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

// Currency
const currencyCode = ref('ILS');
const currency = (n: number): string =>
  Intl.NumberFormat(undefined, { style: 'currency', currency: currencyCode.value }).format(n);

// Labels
const yearlyLabels = computed(() => detailedStats.value?.yearly_stats.map(y => y.period_label).reverse() ?? []);
const monthlyLabels = computed(() => detailedStats.value?.monthly_stats.map(m => m.period_label).reverse() ?? []);

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

// Default latest period
watch([detailedStats, viewMode], () => {
  const ds = detailedStats.value;
  if (!ds) return;
  if (viewMode.value === 'yearly') {
    const labels = yearlyLabels.value;
    if (labels.length) selectedPeriod.value = labels[labels.length - 1];
  } else {
    const labels = monthlyLabels.value;
    if (labels.length) selectedPeriod.value = labels[labels.length - 1];
  }
}, { immediate: true });

// Selected rows
const selectedYearRow = computed(() =>
  viewMode.value === 'yearly'
    ? detailedStats.value?.yearly_stats.find(y => y.period_label === selectedPeriod.value) ?? null
    : null
);
const selectedMonthRow = computed(() =>
  viewMode.value === 'monthly'
    ? detailedStats.value?.monthly_stats.find(m => m.period_label === selectedPeriod.value) ?? null
    : null
);

// Header
const headerPeriodLabel = computed(() => {
  const ds = detailedStats.value;
  if (!ds) return 'Period: —';
  const firstYear = ds.yearly_stats[0]?.period_label ?? '—';
  const lastYear = ds.yearly_stats[ds.yearly_stats.length - 1]?.period_label ?? '—';
  return `Period: ${firstYear} – ${lastYear}`;
});

// Insight helpers
function efficiencyInsight(value: number, avg: number) {
  if (value > avg * 1.1) return "fuel consumption was higher than usual";
  if (value < avg * 0.9) return "fuel consumption was lower than usual";
  return "fuel consumption was close to average";
}
function distanceInsight(distance: number, avg: number) {
  if (distance > avg * 1.1) return "you drove a lot more than usual";
  if (distance < avg * 0.9) return "you drove less than you normally do";
  return "your driving distance was typical";
}

// Yearly insights
const insightsYearlySelected = computed<string>(() => {
  const ds = detailedStats.value;
  const row = selectedYearRow.value;
  if (!ds || !row) return "";
  const avgEff = ds.yearly_stats.reduce((s, y) => s + y.average_km_per_liter, 0) / ds.yearly_stats.length;
  const avgDist = ds.yearly_stats.reduce((s, y) => s + y.total_distance, 0) / ds.yearly_stats.length;
  return `During ${row.period_label}, ${efficiencyInsight(row.average_km_per_liter, avgEff)} and ${distanceInsight(row.total_distance, avgDist)}, making this period stand out compared to your usual driving.`;
});

// Monthly insights
const insightsMonthlySelected = computed<string>(() => {
  const ds = detailedStats.value;
  const row = selectedMonthRow.value;
  if (!ds || !row) return "";
  const avgEff = ds.monthly_stats.reduce((s, m) => s + m.average_km_per_liter, 0) / ds.monthly_stats.length;
  const avgDist = ds.monthly_stats.reduce((s, m) => s + m.total_distance, 0) / ds.monthly_stats.length;
  return `In ${row.period_label}, ${efficiencyInsight(row.average_km_per_liter, avgEff)} and ${distanceInsight(row.total_distance, avgDist)}, giving the month its own driving profile.`;
});

// Chart refs
const yearlyEfficiencyCanvas = ref<HTMLCanvasElement | null>(null);
const yearlyCostCanvas = ref<HTMLCanvasElement | null>(null);
const monthlyEfficiencyCanvas = ref<HTMLCanvasElement | null>(null);
const monthlyCostCanvas = ref<HTMLCanvasElement | null>(null);
const yearlyDistanceCanvas = ref<HTMLCanvasElement | null>(null);
const monthlyDistanceCanvas = ref<HTMLCanvasElement | null>(null);

// ADD: histogram ref
const efficiencyHistogramCanvas = ref<HTMLCanvasElement | null>(null);

// Chart instances
let yearlyEfficiencyChart: ChartJS | null = null;
let yearlyCostChart: ChartJS | null = null;
let monthlyEfficiencyChart: ChartJS | null = null;
let monthlyCostChart: ChartJS | null = null;
let yearlyDistanceChart: ChartJS | null = null;
let monthlyDistanceChart: ChartJS | null = null;

// ADD: histogram chart instance
let efficiencyHistogramChart: ChartJS | null = null;

// Chart options
function chartOptionsWithUnit(yLabel: string, title: string): ChartOptions {
  return {
    responsive: true,
    animation: false,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      title: { display: true, text: title, color: 'var(--color-text)', font: { size: 16 } }
    },
    scales: {
      x: { title: { display: true, text: 'Period', color: 'var(--color-text)' } },
      y: { title: { display: true, text: yLabel, color: 'var(--color-text)' } }
    }
  };
}
function arraysChanged(a: unknown[], b: unknown[]) {
  if (a.length !== b.length) return true;
  return a.some((val, i) => val !== b[i]);
}
function buildDataset(type: 'bar' | 'line', data: number[], color: string) {
  return type === 'bar'
    ? { data, backgroundColor: color }
    : { data, borderColor: color, tension: 0.3, fill: false };
}
function initOrUpdateChart(
  chart: ChartJS | null,
  canvas: HTMLCanvasElement | null,
  type: ChartType,
  labels: string[],
  data: number[],
  dataset: any,
  options: ChartOptions
): ChartJS | null {
  if (!chart && canvas) {
    return new ChartJS(canvas, { type, data: { labels, datasets: [dataset] }, options });
  } else if (chart) {
    const needUpdate =
      arraysChanged(chart.data.labels as string[], labels) ||
      arraysChanged(chart.data.datasets[0].data as number[], data);
    if (needUpdate) {
      chart.data.labels = labels;
      chart.data.datasets[0].data = data;
      chart.options = options;
      chart.update();
    }
  }
  return chart;
}

// Reset helper
function resetCharts() {
  yearlyEfficiencyChart?.destroy();
  yearlyCostChart?.destroy();
  yearlyDistanceChart?.destroy();
  monthlyEfficiencyChart?.destroy();
  monthlyCostChart?.destroy();
  monthlyDistanceChart?.destroy();

  yearlyEfficiencyChart = null;
  yearlyCostChart = null;
  yearlyDistanceChart = null;
  monthlyEfficiencyChart = null;
  monthlyCostChart = null;
  monthlyDistanceChart = null;
}

// Watcher for charts
watch([detailedStats, viewMode, selectedPeriod], async ([ds]) => {
  if (!ds || !selectedPeriod.value) return;
  await nextTick();

  // reset before re‑init
  resetCharts();

  if (viewMode.value === 'yearly' && selectedYearRow.value) {
    const yearKey = selectedYearRow.value.period_label;
    const monthsForYear = ds.monthly_stats.filter(m => m.period_label.startsWith(yearKey)).reverse();

    const labels = monthsForYear.map(m => m.period_label);
    const effData = monthsForYear.map(m => m.average_km_per_liter);
    const costData = monthsForYear.map(m => m.total_cost);
    const distData = monthsForYear.map(m => m.total_distance);

    yearlyEfficiencyChart = initOrUpdateChart(
      yearlyEfficiencyChart, yearlyEfficiencyCanvas.value, 'line',
      labels, effData,
      buildDataset('line', effData, '#2196F3'),
      chartOptionsWithUnit('km/L', `Fuel Efficiency in ${yearKey}`)
    );

    yearlyCostChart = initOrUpdateChart(
      yearlyCostChart, yearlyCostCanvas.value, 'line',
      labels, costData,
      buildDataset('line', costData, '#FF9800'),
      chartOptionsWithUnit(currencyCode.value, `Fuel Cost in ${yearKey}`)
    );

    yearlyDistanceChart = initOrUpdateChart(
      yearlyDistanceChart, yearlyDistanceCanvas.value, 'line',
      labels, distData,
      buildDataset('line', distData, '#9C27B0'),
      chartOptionsWithUnit('km', `Distance Travelled in ${yearKey}`)
    );
  }

  if (viewMode.value === 'monthly' && selectedMonthRow.value) {
    const monthKey = selectedMonthRow.value.period_label;
    const entriesForMonth = store.entries.filter(e =>
      e.date?.startsWith(monthKey)
    ).reverse();

    const labels = entriesForMonth.map(e => e.date!);
    const effData = entriesForMonth.map(e => e.km_per_liter);
    const costData = entriesForMonth.map(e => e.total_cost);
    const distData = entriesForMonth.map(e => e.distance);

    monthlyEfficiencyChart = initOrUpdateChart(
      monthlyEfficiencyChart, monthlyEfficiencyCanvas.value, 'bar',
      labels, effData,
      buildDataset('bar', effData, '#4CAF50'),
      chartOptionsWithUnit('km/L', `Fuel Efficiency for ${monthKey}`)
    );

    monthlyCostChart = initOrUpdateChart(
      monthlyCostChart, monthlyCostCanvas.value, 'bar',
      labels, costData,
      buildDataset('bar', costData, '#FF9800'),
      chartOptionsWithUnit(currencyCode.value, `Fuel Cost for ${monthKey}`)
    );

    monthlyDistanceChart = initOrUpdateChart(
      monthlyDistanceChart, monthlyDistanceCanvas.value, 'bar',
      labels, distData,
      buildDataset('bar', distData, '#9C27B0'),
      chartOptionsWithUnit('km', `Distance Travelled in ${monthKey}`)
    );
  }
}, { immediate: true });

// --- Histogram logic ---
function computeEfficiencyHistogramBins(): { labels: string[]; counts: number[] } {
  const entries = store.entries;
  if (!entries?.length) return { labels: [], counts: [] };

  const efficiencies = entries
    .filter(e => e.distance && e.liters)
    .map(e => e.distance / e.liters);

  if (!efficiencies.length) return { labels: [], counts: [] };

  const minEff = Math.floor(Math.min(...efficiencies) / 2) * 2;
  const maxEff = Math.ceil(Math.max(...efficiencies) / 2) * 2;

  const labels: string[] = [];
  const counts: number[] = [];

  for (let b = minEff; b < maxEff; b += 2) {
    labels.push(`${b}–${b + 2} km/L`);
    counts.push(efficiencies.filter(v => v >= b && v < b + 2).length);
  }

  return { labels, counts };
}

function buildGlobalEfficiencyHistogram() {
  const { labels, counts } = computeEfficiencyHistogramBins();
  if (!efficiencyHistogramCanvas.value) return;

  efficiencyHistogramChart = initOrUpdateChart(
    efficiencyHistogramChart,
    efficiencyHistogramCanvas.value,
    'bar',
    labels,
    counts,
    { data: counts, backgroundColor: '#607D8B' },
    chartOptionsWithUnit('Count', 'Fuel Efficiency Distribution')
  );
}

// Watcher for histogram
watch([detailedStats, () => store.entries], async () => {
  await nextTick();
  buildGlobalEfficiencyHistogram();
}, { immediate: true });

// Cleanup on unmount
onUnmounted(() => {
  resetCharts();
  efficiencyHistogramChart?.destroy();
  efficiencyHistogramChart = null;

});
</script>

<style scoped>
/* ==========================================================================
   Report container
   ========================================================================== */

.report-container {
  margin: 0 auto;
  width: 100%;
  max-width: none;
  font-family: var(--font-base);
  color: var(--color-text);
}

/* ==========================================================================
   Header
   ========================================================================== */

.report__header {
  text-align: center;
  margin-bottom: var(--space-lg);
}

.report__title {
  font-size: var(--font-size-xl);
  font-weight: 700;
  margin: 0;
  color: var(--color-text-strong);
}

.report__subtitle {
  margin: 0;
  color: var(--color-text);
}

/* ==========================================================================
   Separator
   ========================================================================== */

.report__separator {
  border: none;
  border-top: 2px solid var(--color-border);
  margin: var(--space-lg) 0;
}

/* ==========================================================================
   Section blocks
   ========================================================================== */

.report__block {
  background: var(--color-card);
  border-radius: var(--radius-lg);
  padding: var(--space-md);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  margin-bottom: var(--space-lg);
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

/* ==========================================================================
   Section headings
   ========================================================================== */

.report__heading {
  font-size: 1.4rem;
  font-weight: 600;
  margin-bottom: var(--space-sm);
  color: var(--color-text-strong);
  border-bottom: 2px solid var(--color-accent);
  padding-bottom: var(--space-xs);
}

/* ==========================================================================
   Lists
   ========================================================================== */

.report__list {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  list-style: disc;
  padding-left: var(--space-md);
  margin: 0;
}

.report__list-item {
  margin-bottom: var(--space-xs);
  font-size: var(--font-size-md);
  color: var(--color-text);
}

/* ==========================================================================
   Charts
   ========================================================================== */

.report__chart {
  width: 100%;
  height: 300px;
  margin: var(--space-lg) 0;
}

.report__chart-canvas {
  width: 100% !important;
  height: 100% !important;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-input-bg);
  padding: var(--space-xs);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

/* ==========================================================================
   Tables
   ========================================================================== */

.report__table {
  width: 100%;
  border-collapse: collapse;
  margin: var(--space-lg) 0;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  overflow: hidden;
}

.report__table-head th {
  text-align: left;
  font-weight: 600;
  color: var(--color-text-strong);
  background: var(--color-row-light);
  font-size: var(--font-size-sm);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.report__table th,
.report__table td {
  padding: var(--space-xs);
  border-bottom: 1px solid var(--color-border);
  color: var(--color-text);
}

.report__table tbody tr:nth-child(odd) {
  background-color: var(--color-row-light);
}

.report__table tbody tr:nth-child(even) {
  background-color: var(--color-row-dark);
}

.report__table tbody tr:hover {
  background-color: var(--color-row-hover);
  transition: background-color var(--transition-fast);
}

/* ==========================================================================
   Print styles
   ========================================================================== */

@media print {
  .report-container {
    max-width: none;
    margin: 0;
    padding: 0;
    color: #000;
  }

  .report__header {
    text-align: center;
    margin-bottom: 12pt;
  }

  .report__chart {
    height: 240px;
    margin: 12pt 0;
  }

  .report__chart-canvas {
    border: 1pt solid #000;
    box-shadow: none;
  }

  .report__table {
    border: 1pt solid #000;
    margin: 12pt 0;
  }

  .report__table th,
  .report__table td {
    border-bottom: 1pt solid #000;
  }

  .report__block,
  .report__list {
    page-break-inside: avoid;
  }
}
</style>