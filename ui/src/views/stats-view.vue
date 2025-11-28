<!-- ui/src/views/stats-view.vue -->
<template>
   <section class="stats">
    <h1 class="view__headline">📊Stats</h1>
  </section>
  <div class="report-container">

    <!-- Controls -->
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

    <hr class="field__separator" />

    <!-- Executive Summary -->
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
    <hr v-if="summaryBlock" class="field__separator" />

    <!-- Yearly charts -->
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

    <!-- Insights -->
    <section v-if="viewMode === 'yearly' && insightsYearlySelected" class="report__block">
      <h2 class="report__heading">Insights</h2>
      <p class="report__insight">{{ insightsYearlySelected.efficiency }}</p>
      <p class="report__insight">{{ insightsYearlySelected.distance }}</p>
    </section>

    <!-- Monthly charts -->
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

    <!-- Insights -->
    <section v-if="viewMode === 'monthly' && insightsMonthlySelected" class="report__block">
      <h2 class="report__heading">Insights</h2>
      <p class="report__insight">{{ insightsMonthlySelected.efficiency }}</p>
      <p class="report__insight">{{ insightsMonthlySelected.distance }}</p>
    </section>

    <!-- Histogram -->
    <section v-if="detailedStats" class="report__block">
      <h2 class="report__heading">Fuel Efficiency Distribution</h2>
      <div class="report__chart">
        <canvas ref="efficiencyHistogramCanvas" class="report__chart-canvas"></canvas>
      </div>
    </section>
  </div>
</template>


<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, onUpdated, nextTick } from 'vue';
import { useFuelStore } from '../stores/fuel-store';
import type { DetailedStats } from '../types/fuel-entry';

import {
  chartOptionsWithUnit,
  buildDataset,
  initOrUpdateChart,
  resetCharts,
  buildGlobalEfficiencyHistogram
} from '../composables/useChart';

import {
  useSummaryBlock,
  efficiencyInsight,
  distanceInsight,
  usePeriodLabels,
  computeHeaderPeriodLabel
} from '../composables/useStats';

// store and state
const store = useFuelStore();
const detailedStats = computed<DetailedStats | null>(() => store.detailedStats ?? null);

const viewMode = ref<'yearly' | 'monthly'>('yearly');
const selectedPeriod = ref<string | null>(null);
const currencyCode = ref('ILS');

// labels + header
const { yearlyLabels, monthlyLabels } = usePeriodLabels(detailedStats);
const headerPeriodLabel = computed(() => computeHeaderPeriodLabel(detailedStats));

// selected rows
const selectedYearRow = computed(() =>
  detailedStats.value?.yearly_stats.find(y => y.period_label === selectedPeriod.value) ?? null
);
const selectedMonthRow = computed(() =>
  detailedStats.value?.monthly_stats.find(m => m.period_label === selectedPeriod.value) ?? null
);

// summary block
const { summaryBlock } = useSummaryBlock(viewMode, selectedYearRow, selectedMonthRow, currencyCode);

// insights
const insightsYearlySelected = computed(() => {
  const row = selectedYearRow.value;
  const ds = detailedStats.value;
  if (!row || !ds) return null;
  const avgEff = ds.yearly_stats.reduce((s, y) => s + y.average_km_per_liter, 0) / ds.yearly_stats.length;
  const avgDist = ds.yearly_stats.reduce((s, y) => s + y.total_distance, 0) / ds.yearly_stats.length;
  return {
    efficiency: efficiencyInsight(row.average_km_per_liter, avgEff),
    distance: distanceInsight(row.total_distance, avgDist)
  };
});
const insightsMonthlySelected = computed(() => {
  const row = selectedMonthRow.value;
  const ds = detailedStats.value;
  if (!row || !ds) return null;
  const yearKey = row.period_label.slice(0, 4);
  const monthsSameYear = ds.monthly_stats.filter(m => m.period_label.startsWith(yearKey));
  const avgEff = monthsSameYear.reduce((s, m) => s + m.average_km_per_liter, 0) / monthsSameYear.length;
  const avgDist = monthsSameYear.reduce((s, m) => s + m.total_distance, 0) / monthsSameYear.length;
  return {
    efficiency: efficiencyInsight(row.average_km_per_liter, avgEff),
    distance: distanceInsight(row.total_distance, avgDist)
  };
});

// chart refs
const yearlyEfficiencyCanvas = ref<HTMLCanvasElement | null>(null);
const yearlyCostCanvas = ref<HTMLCanvasElement | null>(null);
const yearlyDistanceCanvas = ref<HTMLCanvasElement | null>(null);
const monthlyEfficiencyCanvas = ref<HTMLCanvasElement | null>(null);
const monthlyCostCanvas = ref<HTMLCanvasElement | null>(null);
const monthlyDistanceCanvas = ref<HTMLCanvasElement | null>(null);
const efficiencyHistogramCanvas = ref<HTMLCanvasElement | null>(null);

// chart instances
let yearlyEfficiencyChart: any = null;
let yearlyCostChart: any = null;
let yearlyDistanceChart: any = null;
let monthlyEfficiencyChart: any = null;
let monthlyCostChart: any = null;
let monthlyDistanceChart: any = null;
let histogramChart: any = null;

// ensure latest period is selected
const selectLatestPeriod = () => {
  if (viewMode.value === 'yearly' && yearlyLabels.value.length > 0) {
    selectedPeriod.value = yearlyLabels.value[yearlyLabels.value.length - 1];
  } else if (viewMode.value === 'monthly' && monthlyLabels.value.length > 0) {
    selectedPeriod.value = monthlyLabels.value[monthlyLabels.value.length - 1];
  }
};

// --- FIXED draw functions ---
function drawYearly(ds: DetailedStats) {
  if (!selectedYearRow.value) return;
  const yearKey = selectedYearRow.value.period_label;
  const monthsForYear = ds.monthly_stats.filter(m => m.period_label.startsWith(yearKey)).reverse();

  const labels = monthsForYear.map(m => m.period_label);
  const effData = monthsForYear.map(m => m.average_km_per_liter);
  const costData = monthsForYear.map(m => m.total_cost);
  const distData = monthsForYear.map(m => m.total_distance);

  yearlyEfficiencyChart = initOrUpdateChart(
    yearlyEfficiencyChart,
    yearlyEfficiencyCanvas.value,
    'line',
    labels,
    effData,
    buildDataset('line', effData, '#4CAF50'),
    chartOptionsWithUnit('km/L', `Fuel Efficiency in ${yearKey}`)
  );

  yearlyCostChart = initOrUpdateChart(
    yearlyCostChart,
    yearlyCostCanvas.value,
    'line',
    labels,
    costData,
    buildDataset('line', costData, '#2196F3'),
    chartOptionsWithUnit('Cost', `Fuel Cost in ${yearKey}`)
  );

  yearlyDistanceChart = initOrUpdateChart(
    yearlyDistanceChart,
    yearlyDistanceCanvas.value,
    'line',
    labels,
    distData,
    buildDataset('line', distData, '#FFC107'),
    chartOptionsWithUnit('Distance', `Distance Driven in ${yearKey}`)
  );
}

function drawMonthly(ds: DetailedStats) {
  if (!selectedMonthRow.value) return;
  const monthKey = selectedMonthRow.value.period_label;
  const entriesForMonth = store.entries.filter(e => e.date?.startsWith(monthKey)).reverse();

  const labels = entriesForMonth.map(e => e.date!);
  const effData = entriesForMonth.map(e => e.km_per_liter);
  const costData = entriesForMonth.map(e => e.total_cost);
  const distData = entriesForMonth.map(e => e.distance);

  monthlyEfficiencyChart = initOrUpdateChart(
    monthlyEfficiencyChart,
    monthlyEfficiencyCanvas.value,
    'bar',
    labels,
    effData,
    buildDataset('bar', effData, '#4CAF50'),
    chartOptionsWithUnit('km/L', `Fuel Efficiency for ${monthKey}`)
  );

  monthlyCostChart = initOrUpdateChart(
    monthlyCostChart,
    monthlyCostCanvas.value,
    'bar',
    labels,
    costData,
    buildDataset('bar', costData, '#2196F3'),
    chartOptionsWithUnit('Cost', `Fuel Cost for ${monthKey}`)
  );

  monthlyDistanceChart = initOrUpdateChart(
    monthlyDistanceChart,
    monthlyDistanceCanvas.value,
    'bar',
    labels,
    distData,
    buildDataset('bar', distData, '#FFC107'),
    chartOptionsWithUnit('Distance', `Distance Driven in ${monthKey}`)
  );
}

function drawHistogram() {
  if (efficiencyHistogramCanvas.value && store.entries?.length) {
    histogramChart = buildGlobalEfficiencyHistogram(
      histogramChart,
      efficiencyHistogramCanvas.value,
      store.entries
    );
  }
}

// lifecycle
onMounted(async () => {
  selectLatestPeriod();
  await nextTick(); // ensure canvases exist
  if (detailedStats.value) {
    if (viewMode.value === 'yearly') drawYearly(detailedStats.value);
    else drawMonthly(detailedStats.value);
  }
  drawHistogram();
});

// redraw when stats or viewMode change, after DOM updates
watch([detailedStats, viewMode], async ([ds]) => {
  if (!ds) return;
  await nextTick();
  if (viewMode.value === 'yearly') drawYearly(ds);
  else drawMonthly(ds);
}, { immediate: true });

// keep selectedPeriod in sync with labels and mode
watch([viewMode, yearlyLabels, monthlyLabels], () => {
  selectLatestPeriod();
}, { immediate: true });

// histogram: update when entries change and after DOM updates
watch(
  () => store.entries,
  async entries => {
    await nextTick();
    drawHistogram();
  },
  { deep: true, immediate: true }
);

// also re-draw after any template update (e.g., toggling yearly/monthly swaps canvases)
onUpdated(async () => {
  await nextTick();
  if (detailedStats.value) {
    if (viewMode.value === 'yearly') drawYearly(detailedStats.value);
    else drawMonthly(detailedStats.value);
  }
  drawHistogram();
});

// optional cleanup on unmount
onUnmounted(() => {
  resetCharts([
    yearlyEfficiencyChart,
    yearlyCostChart,
    yearlyDistanceChart,
    monthlyEfficiencyChart,
    monthlyCostChart,
    monthlyDistanceChart,
    histogramChart
  ]);
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
   Section blocks
   ========================================================================== */

.report__block {
  background: var(--color-card);
  border-radius: var(--radius-lg);
  padding: var(--space-md);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  margin-top: var(--space-lg);
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
  width: 100%;
  height: 300px; /* fixed height */
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