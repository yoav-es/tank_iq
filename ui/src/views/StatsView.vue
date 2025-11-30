<!-- ui/src/views/stats-view.vue -->
<template>
    <section class="stats">
      <h1 class="headline">📊 Stats</h1>
    </section>

    <div class="report-container">
      <!-- Summary (renamed, controls moved here) -->
    <section v-if="summaryBlock" class="panel report__block">
      <h2 class="report__heading">General Summary</h2>
      <p>
        {{ summaryBlock.periodText }}. During this time, vehicles covered {{ summaryBlock.totalDistance }} km, 
        reflecting overall usage across the fleet. Average efficiency was {{ summaryBlock.averageEfficiency }} km/L, 
        offering a clear measure of performance and fuel utilization. Spending reached {{ summaryBlock.totalCost }}, 
        shaped by both fuel prices and consumption levels. Compared to earlier periods, efficiency was 
        {{ summaryBlock.efficiencyCompare }}, while costs {{ summaryBlock.costCompare }}, highlighting shifts in 
        driving habits, maintenance, or external conditions. Together, these figures provide a concise overview of 
        operational trends and point to areas worth monitoring in the future.
      </p>

    <!-- Controls moved under summary -->
    <div class="btn-group u-flex u-gap-md u-align-center">
      <!-- Toggle buttons -->
      <button
        class="btn"
        :class="{ 'btn-primary': viewMode === 'yearly' }"
        @click="viewMode = 'yearly'"
      >
        Yearly
      </button>
      <button
        class="btn"
        :class="{ 'btn-primary': viewMode === 'monthly' }"
        @click="viewMode = 'monthly'"
      >
        Monthly
      </button>

      <!-- Period selector inline -->
      <div class="period-control u-flex u-gap-sm u-align-center">
        <span class="period-label">Period:</span>
        <select v-model="selectedPeriod" class="select period-select">
          <option
            v-for="opt in (viewMode === 'yearly' ? yearlyLabels : monthlyLabels)"
            :key="opt"
            :value="opt"
          >
            {{ opt }}
          </option>
        </select>
      </div>
    </div>

  </section>



    <hr v-if="summaryBlock" class="field__separator" />

    <!-- Yearly charts -->
    <section v-if="viewMode === 'yearly' && detailedStats" class="panel report__block">
      <h2 class="report__heading">Yearly Fuel Efficiency Trends</h2>
      <div class="report__chart">
        <canvas ref="yearlyEfficiencyCanvas" class="report__chart-canvas"></canvas>
      </div>
    </section>
    <section v-if="viewMode === 'yearly' && detailedStats" class="panel report__block">
      <h2 class="report__heading">Yearly Fuel Cost Trends</h2>
      <div class="report__chart">
        <canvas ref="yearlyCostCanvas" class="report__chart-canvas"></canvas>
      </div>
    </section>
    <section v-if="viewMode === 'yearly' && detailedStats" class="panel report__block">
      <h2 class="report__heading">Yearly Distance Trends</h2>
      <div class="report__chart">
        <canvas ref="yearlyDistanceCanvas" class="report__chart-canvas"></canvas>
      </div>
    </section>

    <!-- Expanded Yearly Insights -->
    <section v-if="viewMode === 'yearly' && insightsYearlySelected" class="panel report__block">
      <h2 class="report__heading">Insights</h2>
      <p class="report__insight">
        Efficiency this year showed {{ insightsYearlySelected.efficiency }},
        suggesting that driving habits and vehicle performance have shifted compared to previous years.
      </p>
      <p class="report__insight">
        Distance traveled {{ insightsYearlySelected.distance }},
        which highlights how usage patterns are evolving and may influence future fuel needs.
      </p>
    </section>

    <!-- Monthly charts -->
    <section v-if="viewMode === 'monthly' && detailedStats" class="panel report__block">
      <h2 class="report__heading">Monthly Fuel Efficiency Trends</h2>
      <div class="report__chart">
        <canvas ref="monthlyEfficiencyCanvas" class="report__chart-canvas"></canvas>
      </div>
    </section>
    <section v-if="viewMode === 'monthly' && detailedStats" class="panel report__block">
      <h2 class="report__heading">Monthly Fuel Cost Trends</h2>
      <div class="report__chart">
        <canvas ref="monthlyCostCanvas" class="report__chart-canvas"></canvas>
      </div>
    </section>
    <section v-if="viewMode === 'monthly' && detailedStats" class="panel report__block">
      <h2 class="report__heading">Monthly Distance Trends</h2>
      <div class="report__chart">
        <canvas ref="monthlyDistanceCanvas" class="report__chart-canvas"></canvas>
      </div>
    </section>

    <!-- Expanded Monthly Insights -->
    <section v-if="viewMode === 'monthly' && insightsMonthlySelected" class="panel report__block">
      <h2 class="report__heading">Insights</h2>
      <p class="report__insight">
        Monthly efficiency trends indicate {{ insightsMonthlySelected.efficiency }},
        pointing to seasonal factors or maintenance cycles that affect performance.
      </p>
      <p class="report__insight">
        Distance covered {{ insightsMonthlySelected.distance }},
        offering a clearer picture of how travel intensity varies month to month.
      </p>
    </section>

    <!-- Histogram -->
    <section v-if="detailedStats" class="panel report__block">
      <h2 class="report__heading">Fuel Efficiency Distribution</h2>
      <div class="report__chart">
        <canvas ref="efficiencyHistogramCanvas" class="report__chart-canvas"></canvas>
      </div>
    </section>
  </div>
</template>



<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue';
import { useFuelStore } from '../stores/fuelStore';
import type { DetailedStats } from '../types/FuelEntry';
import type { Chart } from 'chart.js';

import {
  getLabels,
  getData,
  getCostData,
  getDistanceData,
  buildDataset,
  initOrUpdateChart,
  resetCharts,
  buildGlobalEfficiencyHistogram,
  buildOptions
} from '../composables/useChart';

import {
  useSummaryBlock,
  efficiencyInsight,
  distanceInsight,
  usePeriodLabels,
  computeHeaderPeriodLabel
} from '../composables/useStats';

/**
 * Store and reactive state
 */
const store = useFuelStore();
const detailedStats = computed<DetailedStats | null>(() => store.detailedStats ?? null);

const viewMode = ref<'yearly' | 'monthly'>('yearly');   // ✅ matches useChart.ts
const selectedPeriod = ref<string | null>(null);
const currencyCode = ref('ILS');

/**
 * Labels + header
 */
const { yearlyLabels, monthlyLabels } = usePeriodLabels(detailedStats);
const headerPeriodLabel = computed(() => computeHeaderPeriodLabel(detailedStats));

/**
 * Selected rows
 */
const selectedYearRow = computed(() =>
  detailedStats.value?.yearly_stats.find(y => y.period_label === selectedPeriod.value) ?? null
);
const selectedMonthRow = computed(() =>
  detailedStats.value?.monthly_stats.find(m => m.period_label === selectedPeriod.value) ?? null
);

/**
 * Summary block
 */
const { summaryBlock } = useSummaryBlock(viewMode, selectedYearRow, selectedMonthRow, currencyCode);

/**
 * Insights
 */
const insightsYearlySelected = computed(() => {
  const row = selectedYearRow.value;
  const ds = detailedStats.value;
  if (!row || !ds?.yearly_stats?.length) return null;

  const avgEff = ds.yearly_stats.reduce((s, y) => s + (y.average_km_per_liter ?? 0), 0) / ds.yearly_stats.length;
  const avgDist = ds.yearly_stats.reduce((s, y) => s + (y.total_distance ?? 0), 0) / ds.yearly_stats.length;

  return {
    efficiency: efficiencyInsight(row.average_km_per_liter ?? 0, avgEff),
    distance: distanceInsight(row.total_distance ?? 0, avgDist)
  };
});

const insightsMonthlySelected = computed(() => {
  const row = selectedMonthRow.value;
  const ds = detailedStats.value;
  if (!row || !ds?.monthly_stats?.length) return null;

  const yearKey = row.period_label?.slice(0, 4);
  if (!yearKey) return null;

  const monthsSameYear = ds.monthly_stats.filter(m => m.period_label?.startsWith(yearKey));
  if (!monthsSameYear.length) return null;

  const avgEff = monthsSameYear.reduce((s, m) => s + (m.average_km_per_liter ?? 0), 0) / monthsSameYear.length;
  const avgDist = monthsSameYear.reduce((s, m) => s + (m.total_distance ?? 0), 0) / monthsSameYear.length;

  return {
    efficiency: efficiencyInsight(row.average_km_per_liter ?? 0, avgEff),
    distance: distanceInsight(row.total_distance ?? 0, avgDist)
  };
});

/**
 * Chart canvas refs
 */
const yearlyEfficiencyCanvas = ref<HTMLCanvasElement | null>(null);
const yearlyCostCanvas = ref<HTMLCanvasElement | null>(null);
const yearlyDistanceCanvas = ref<HTMLCanvasElement | null>(null);
const monthlyEfficiencyCanvas = ref<HTMLCanvasElement | null>(null);
const monthlyCostCanvas = ref<HTMLCanvasElement | null>(null);
const monthlyDistanceCanvas = ref<HTMLCanvasElement | null>(null);
const efficiencyHistogramCanvas = ref<HTMLCanvasElement | null>(null);

/**
 * Chart instances
 */
let yearlyEfficiencyChart: Chart | null = null;
let yearlyCostChart: Chart | null = null;
let yearlyDistanceChart: Chart | null = null;
let monthlyEfficiencyChart: Chart | null = null;
let monthlyCostChart: Chart | null = null;
let monthlyDistanceChart: Chart | null = null;
let histogramChart: Chart | null = null;

/**
 * Ensure latest period is selected
 */
const selectLatestPeriod = () => {
  if (viewMode.value === 'yearly' && yearlyLabels.value.length > 0) {
    selectedPeriod.value = yearlyLabels.value.at(-1) ?? null;
  } else if (viewMode.value === 'monthly' && monthlyLabels.value.length > 0) {
    selectedPeriod.value = monthlyLabels.value.at(-1) ?? null;
  }
};

/**
 * Draw functions
 */
function drawYearly(ds: DetailedStats) {
  if (!selectedPeriod.value) return;

  // ✅ Filter monthly aggregates for the selected year
  let monthsOfYear = (ds.monthly_stats ?? []).filter(m =>
    m.period_label?.startsWith(selectedPeriod.value!)
  );

  // ✅ Ensure chronological order (Jan → Dec)
  monthsOfYear.sort((a, b) => String(a.period_label).localeCompare(String(b.period_label)));

  const labels = getLabels('month', monthsOfYear);
  const effData = getData(monthsOfYear);
  yearlyEfficiencyChart = initOrUpdateChart(
    yearlyEfficiencyChart,
    yearlyEfficiencyCanvas.value,
    'line',
    labels,
    effData,
    buildDataset('line', effData, '#10B981'),
    buildOptions('month', 'Efficiency (km/L)', `Efficiency in ${selectedPeriod.value}`)
  );

  const costData = getCostData(monthsOfYear);
  yearlyCostChart = initOrUpdateChart(
    yearlyCostChart,
    yearlyCostCanvas.value,
    'bar',
    labels,
    costData,
    buildDataset('bar', costData, '#3B82F6'),
    buildOptions('month', 'Total Cost', `Fuel Cost in ${selectedPeriod.value}`)
  );

  const distData = getDistanceData(monthsOfYear);
  yearlyDistanceChart = initOrUpdateChart(
    yearlyDistanceChart,
    yearlyDistanceCanvas.value,
    'bar',
    labels,
    distData,
    buildDataset('bar', distData, '#F59E0B'),
    buildOptions('month', 'Distance (km)', `Distance in ${selectedPeriod.value}`)
  );
}

function drawMonthly(ds: DetailedStats) {
  if (!selectedPeriod.value) return;

  // ✅ Filter raw entries for the selected month (YYYY-MM)
  let entriesOfMonth = store.entries.filter(e =>
    e.date?.startsWith(selectedPeriod.value!)
  );

  // ✅ Ensure chronological order (old → new)
  entriesOfMonth.sort((a, b) => String(a.date).localeCompare(String(b.date)));

  // ✅ Build labels and data from raw entries
  const labels = entriesOfMonth
    .map(e => e.date)
    .filter((d): d is string => !!d); // remove nulls

  const effData = entriesOfMonth.map(e =>
    e.liters ? e.distance / e.liters : 0
  );
  const costData = entriesOfMonth.map(e => e.total_cost ?? 0);
  const distData = entriesOfMonth.map(e => e.distance ?? 0);

  monthlyEfficiencyChart = initOrUpdateChart(
    monthlyEfficiencyChart,
    monthlyEfficiencyCanvas.value,
    'bar',
    labels,
    effData,
    buildDataset('bar', effData, '#10B981'),
    buildOptions('month', 'Efficiency (km/L)', `Entries in ${selectedPeriod.value}`)
  );

  monthlyCostChart = initOrUpdateChart(
    monthlyCostChart,
    monthlyCostCanvas.value,
    'bar',
    labels,
    costData,
    buildDataset('bar', costData, '#3B82F6'),
    buildOptions('month', 'Cost', `Entries in ${selectedPeriod.value}`)
  );

  monthlyDistanceChart = initOrUpdateChart(
    monthlyDistanceChart,
    monthlyDistanceCanvas.value,
    'bar',
    labels,
    distData,
    buildDataset('bar', distData, '#F59E0B'),
    buildOptions('month', 'Distance (km)', `Entries in ${selectedPeriod.value}`)
  );
}

function drawHistogram() {
  histogramChart = buildGlobalEfficiencyHistogram(
    histogramChart,
    efficiencyHistogramCanvas.value,
    store.entries
  );
}

/**
 * Lifecycle hooks
 */
onMounted(async () => {
  selectLatestPeriod();
  await nextTick();
  if (detailedStats.value) {
    viewMode.value === 'yearly'
      ? drawYearly(detailedStats.value)
      : drawMonthly(detailedStats.value);
  }
  drawHistogram();
});

watch([detailedStats, viewMode, selectedPeriod], async ([ds]) => {
  if (!ds) return;
  await nextTick();
  viewMode.value === 'yearly' ? drawYearly(ds) : drawMonthly(ds);
}, { immediate: true });

watch([viewMode, yearlyLabels, monthlyLabels], () => {
  selectLatestPeriod();
}, { immediate: true });

watch(
  () => store.entries,
  async () => {
    await nextTick();
    drawHistogram();
  },
  { deep: true, immediate: true }
);

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
  yearlyEfficiencyChart = null;
  yearlyCostChart = null;
  yearlyDistanceChart = null;
  monthlyEfficiencyChart = null;
  monthlyCostChart = null;
  monthlyDistanceChart = null;
  histogramChart = null;
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

/* Toggle container */
.btn-group {
  display: flex;
  gap: var(--space-sm);
  align-items: center;
}

/* Inactive toggle buttons */
.btn {
  min-width: 90px;                  /* consistent width */
  height: 36px;                     /* consistent height */
  padding: 0.5rem 1rem;             /* balanced padding */
  border-radius: var(--radius-sm);  /* rounded corners like dashboard */
  background: var(--color-surface);   /* same as dashboard inactive */
  color: var(--color-text);
  border: 1px solid var(--color-border);
  cursor: pointer;
  font-size: var(--font-size-md);
  font-weight: 500;
}

/* Active toggle button */
.btn-primary {
  background: var(--color-primary);   /* same as dashboard active */
  color: var(--color-on-primary);
  border-color: var(--color-primary);
}

/* Period label + select aligned with buttons */
/* Period label + select aligned with buttons */
.period-control {
  display: flex;
  align-items: center;   /* keeps label and select vertically centered */
  gap: var(--space-sm);
}

.period-label {
  color: var(--color-text);
  font-weight: 500;
  font-size: var(--font-size-md);
  line-height: 1.2;      /* normal line height */
  margin-right: var(--space-sm);
}

.period-select {
  min-width: 90px;                  /* consistent width */
  height: 36px;                     /* same as buttons */
  background: var(--color-surface);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  font-size: var(--font-size-md);
  padding: 0.4rem 0.6rem;
  border-radius: var(--radius-md);  /* match button shape */
  display: flex;
  align-items: center;              /* centers text inside select */
}
.period-select:focus {
  border-color: var(--color-primary);
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