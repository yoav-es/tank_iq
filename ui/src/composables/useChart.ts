// ui/src/composables/useChart.ts
import { Chart as ChartJS } from 'chart.js/auto';
import type { ChartOptions, ChartType, ChartData } from 'chart.js';
import { markRaw } from 'vue';

/**
 * Supported modes for statistics visualization.
 * - 'month': monthly stats
 * - 'year': yearly stats
 */
export type Mode = 'month' | 'year';

/**
 * Statistics entry structure (expanded for StatsView needs).
 */
export interface Stat {
  period_label: string;           // e.g. "2025-11" or "2025"
  average_km_per_liter?: number;  // efficiency
  total_cost?: number;            // aggregated cost per period
  total_distance?: number;        // aggregated distance per period
}

/**
 * Data source interface for statistics.
 */
export interface StatsDataSource {
  monthly_stats?: Stat[];
  yearly_stats?: Stat[];
}

/**
 * Check if stats exist for a given mode.
 */
export function hasStats(ds: StatsDataSource | null, mode: Mode): boolean {
  if (!ds) return false;
  const list = mode === 'month' ? ds.monthly_stats : ds.yearly_stats;
  return !!(list && list.length > 0);
}

/**
 * Extract statistics list from data source, sorted by period label.
 */
export function getStats(ds: StatsDataSource | null, mode: Mode): Stat[] {
  if (!ds) return [];
  const list: Stat[] =
    mode === 'month' ? [...(ds.monthly_stats ?? [])] : [...(ds.yearly_stats ?? [])];
  if (!list.length) return [];
  list.sort((a, b) => String(a.period_label).localeCompare(String(b.period_label)));
  return list;
}

/**
 * Build labels for chart based on mode.
 * - Month mode: "MM/YYYY"
 * - Year mode: "YYYY"
 */
export function getLabels(mode: Mode, stats: Stat[]): string[] {
  return stats.map((s) =>
    mode === 'month'
      ? `${String(s.period_label).split('-')[1]}/${String(s.period_label).split('-')[0]}`
      : String(s.period_label)
  );
}

/**
 * Extract numeric efficiency data from statistics (km/L).
 */
export function getData(stats: Stat[]): number[] {
  return stats.map((s) => Number(s.average_km_per_liter ?? 0));
}

/**
 * Extract numeric cost data from statistics.
 */
export function getCostData(stats: Stat[]): number[] {
  return stats.map((s) => Number(s.total_cost ?? 0));
}

/**
 * Extract numeric distance data from statistics.
 */
export function getDistanceData(stats: Stat[]): number[] {
  return stats.map((s) => Number(s.total_distance ?? 0));
}

/**
 * Build a dataset for bar or line charts.
 * - Line charts include a shaded area under the line.
 */
export function buildDataset(
  type: 'bar' | 'line',
  data: number[],
  color: string
): ChartData<'bar' | 'line'>['datasets'][0] {
  return type === 'bar'
    ? { data, backgroundColor: color }
    : {
        data,
        borderColor: color,
        backgroundColor: 'rgba(16, 185, 129, 0.2)', // shaded area under line
        tension: 0.3,
        fill: true
      };
}

/**
 * Utility: compare two arrays for changes.
 */
export function arraysChanged<T>(a: T[], b: T[]): boolean {
  if (a.length !== b.length) return true;
  return a.some((val, i) => val !== b[i]);
}

/**
 * Build chart options with dynamic labels and title.
 * Unified styling for both Dashboard and Stats views using CSS variables.
 */
export function buildOptions(
  mode: Mode | null,
  yLabel: string,
  title: string
): ChartOptions {
  return {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 300 },
    plugins: {
      legend: { display: false },
      title: {
        display: true,
        text: title,
        color: 'var(--color-text)',
        font: { size: 16 }
      }
    },
    scales: {
      x: {
        title: {
          display: true,
          text: mode === 'month' ? 'Month' : mode === 'year' ? 'Year' : 'Period',
          color: 'var(--color-text)'
        },
        ticks: { color: 'var(--color-text)' },
        grid: { color: 'var(--color-muted)' }
      },
      y: {
        title: { display: true, text: yLabel, color: 'var(--color-text)' },
        ticks: { color: 'var(--color-text)' },
        grid: { color: 'var(--color-muted)' }
      }
    }
  };
}

/**
 * Generic initializer/updater for charts.
 * Works for both DashboardView and StatsView.
 *
 * - Creates a new ChartJS instance if none exists.
 * - Updates labels/data/options if they changed.
 * - Safely re-binds to a different canvas if needed.
 */
export function initOrUpdateChart(
  chart: ChartJS | null,
  canvas: HTMLCanvasElement | null,
  type: ChartType,
  labels: string[],
  data: number[],
  dataset: ChartData<'bar' | 'line'>['datasets'][0],
  options: ChartOptions
): ChartJS | null {
  if (!canvas) return chart;

  // If chart exists but is bound to a different canvas, destroy before re-creating
  if (chart && (chart as any).canvas && (chart as any).canvas !== canvas) {
    chart.destroy();
    chart = null;
  }

  // Create chart if missing
  if (!chart) {
    return markRaw(
      new ChartJS(canvas, { type, data: { labels, datasets: [dataset] }, options })
    );
  }

  // Update chart if labels or data changed
  const needUpdate =
    arraysChanged(chart.data.labels as string[], labels) ||
    arraysChanged(chart.data.datasets[0].data as number[], data);

  if (needUpdate) {
    chart.data.labels = labels;
    chart.data.datasets[0].data = data;
    chart.options = options;
    chart.update();
  }

  return chart;
}

/**
 * Compute histogram bins for fuel efficiency values.
 * - Bins are 2 km/L wide for readability.
 * - Returns empty arrays if no valid data.
 */
export function computeEfficiencyHistogramBins(
  entries: { distance?: number; liters?: number }[]
): { labels: string[]; counts: number[] } {
  if (!entries?.length) return { labels: [], counts: [] };

  const efficiencies = entries
    .filter(e => e.distance && e.liters)
    .map(e => e.distance! / e.liters!);

  if (!efficiencies.length) return { labels: [], counts: [] };

  let minEff = Math.floor(Math.min(...efficiencies) / 2) * 2;
  let maxEff = Math.ceil(Math.max(...efficiencies) / 2) * 2;

  if (minEff === maxEff) {
    maxEff = minEff + 2;
  }

  const labels: string[] = [];
  const counts: number[] = [];

  for (let b = minEff; b < maxEff; b += 2) {
    labels.push(`${b}–${b + 2} km/L`);
    counts.push(efficiencies.filter(v => v >= b && v < b + 2).length);
  }

  // If all bins are zero, avoid rendering an empty chart
  if (counts.every(c => c === 0)) {
    return { labels: [], counts: [] };
  }

  return { labels, counts };
}

/**
 * Build or update global efficiency histogram chart.
 * - Destroys chart if no data is available.
 * - Uses unified styling via buildOptions.
 */
export function buildGlobalEfficiencyHistogram(
  chart: ChartJS | null,
  canvas: HTMLCanvasElement | null,
  entries: { distance?: number; liters?: number }[]
): ChartJS | null {
  if (!canvas) return chart;

  const { labels, counts } = computeEfficiencyHistogramBins(entries);

  if (!labels.length || !counts.length) {
    if (chart) chart.destroy();
    return null;
  }

  if (!chart) {
    return new ChartJS(canvas, {
      type: 'bar',
      data: { labels, datasets: [{ data: counts, backgroundColor: '#607D8B' }] },
      options: buildOptions(null, 'Count', 'Fuel Efficiency Distribution')
    });
  } else {
    const needUpdate =
      arraysChanged(chart.data.labels as string[], labels) ||
      arraysChanged(chart.data.datasets[0].data as number[], counts);
    if (needUpdate) {
      chart.data.labels = labels;
      chart.data.datasets[0].data = counts;
      chart.update();
    }
    return chart;
  }
}

/**
 * Reset multiple charts safely.
 * - Destroys chart instances without throwing if null.
 */
export function resetCharts(charts: (ChartJS | null)[]) {
  charts.forEach(c => {
    if (c) c.destroy();
  });
}
