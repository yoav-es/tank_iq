// ui/src/composables/useChart.ts
import { Chart as ChartJS } from 'chart.js/auto';
import type { ChartOptions, ChartType, ChartData } from 'chart.js';
import { markRaw } from 'vue';

// >>> ADDED for dashboard
export type Mode = 'month' | 'year';

/**
 * Build chart options with dynamic labels and title.
 */
export function chartOptionsWithUnit(yLabel: string, title: string): ChartOptions {
  return {
    responsive: true,
    animation: false,
    maintainAspectRatio: false,
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
      x: { title: { display: true, text: 'Period', color: 'var(--color-text)' } },
      y: { title: { display: true, text: yLabel, color: 'var(--color-text)' } }
    }
  };
}

/**
 * Compare two arrays for changes.
 */
export function arraysChanged<T>(a: T[], b: T[]): boolean {
  if (a.length !== b.length) return true;
  return a.some((val, i) => val !== b[i]);
}

/**
 * Build a dataset for bar or line charts.
 */
export function buildDataset(
  type: 'bar' | 'line',
  data: number[],
  color: string
) {
  return type === 'bar'
    ? { data, backgroundColor: color }
    : { data, borderColor: color, tension: 0.3, fill: false };
}

/**
 * Initialize or update a chart instance.
 */
export function initOrUpdateChart(
  chart: ChartJS | null,
  canvas: HTMLCanvasElement | null,
  type: ChartType,
  labels: string[],
  data: number[],
  dataset: any,
  options: ChartOptions
): ChartJS | null {
  if (!canvas) return chart;

  // If we had a chart, but the canvas element was replaced (v-if toggle),
  // destroy the old chart and start fresh on the new canvas.
  if (chart && (chart as any).canvas && (chart as any).canvas !== canvas) {
    chart.destroy();
    chart = null;
  }

  if (!chart) {
    return new ChartJS(canvas, { type, data: { labels, datasets: [dataset] }, options });
  } else {
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
}

/**
 * Destroy all chart instances and reset refs.
 */
export function resetCharts(charts?: any[]) {
  if (!charts) return;
  charts.forEach(c => {
    if (c && typeof c.destroy === 'function') {
      c.destroy();
    }
  });
}

/**
 * Histogram binning logic
 */
export function computeEfficiencyHistogramBins(entries: any[]): { labels: string[]; counts: number[] } {
  if (!entries?.length) return { labels: ['No data'], counts: [0] };

  const efficiencies = entries
    .filter(e => e.distance && e.liters)
    .map(e => e.distance / e.liters);

  if (!efficiencies.length) return { labels: ['No data'], counts: [0] };

  let minEff = Math.floor(Math.min(...efficiencies) / 2) * 2;
  let maxEff = Math.ceil(Math.max(...efficiencies) / 2) * 2;

  // Ensure at least one bin
  if (minEff === maxEff) {
    maxEff = minEff + 2;
  }

  const labels: string[] = [];
  const counts: number[] = [];

  for (let b = minEff; b < maxEff; b += 2) {
    labels.push(`${b}–${b + 2} km/L`);
    counts.push(efficiencies.filter(v => v >= b && v < b + 2).length);
  }

  // fallback if all bins are zero
  if (counts.every(c => c === 0)) {
    return { labels: ['No data'], counts: [0] };
  }

  return { labels, counts };
}

/**
 * Build global efficiency histogram chart
 */
export function buildGlobalEfficiencyHistogram(
  chart: ChartJS | null,
  canvas: HTMLCanvasElement | null,
  entries: any[]
): ChartJS | null {
  if (!canvas) return chart;

  const { labels, counts } = computeEfficiencyHistogramBins(entries);

  if (!chart) {
    return new ChartJS(canvas, {
      type: 'bar',
      data: { labels, datasets: [{ data: counts, backgroundColor: '#607D8B' }] },
      options: chartOptionsWithUnit('Count', 'Fuel Efficiency Distribution')
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

// >>> ADDED for dashboard
export function getStats(ds: any, mode: Mode) {
  const list: any[] =
    mode === 'month' ? [...(ds?.monthly_stats ?? [])] : [...(ds?.yearly_stats ?? [])];
  list.sort((a, b) => String(a.period_label).localeCompare(String(b.period_label)));
  return list;
}

export function getLabels(mode: Mode, stats: any[]): string[] {
  return stats.map((s) =>
    mode === 'month'
      ? `${String(s.period_label).split('-')[1]}/${String(s.period_label).split('-')[0]}`
      : String(s.period_label)
  );
}

export function getData(stats: any[]): number[] {
  return stats.map((s) => Number(s.average_km_per_liter ?? 0));
}

export function buildDashboardOptions(mode: Mode): ChartOptions<'line'> {
  return {
    responsive: true,
    maintainAspectRatio: false,
    layout: { padding: { bottom: 10 } },
    animation: { duration: 300 },
    plugins: { legend: { display: false } },
    scales: {
      x: {
        title: {
          display: true,
          text: mode === 'month' ? 'Month' : 'Year',
          color: '#f1f5f9',
        },
        ticks: { color: '#f1f5f9' },
      },
      y: {
        title: {
          display: true,
          text: 'Efficiency (km/L)',
          color: '#f1f5f9',
        },
        ticks: { color: '#f1f5f9' },
      },
    },
  };
}

export function initDashboardChart(
  canvas: HTMLCanvasElement,
  mode: Mode,
  stats: any[]
): ChartJS<'line'> {
  const labels = getLabels(mode, stats);
  const dataset = getData(stats);

  const data: ChartData<'line'> = {
    labels,
    datasets: [
      {
        label: `Average Efficiency (${mode}) [km/L]`,
        data: dataset,
        borderColor:
          getComputedStyle(document.documentElement).getPropertyValue('--color-secondary').trim() ||
          '#10B981',
        backgroundColor: 'rgba(16, 185, 129, 0.2)',
        fill: true,
        tension: 0.3,
      },
    ],
  };

  return markRaw(
    new ChartJS<'line'>(canvas.getContext('2d')!, {
      type: 'line',
      data,
      options: buildDashboardOptions(mode),
    })
  );
}

export function updateDashboardChart(chart: ChartJS<'line'>, mode: Mode, stats: any[]) {
  chart.data.labels = getLabels(mode, stats);
  chart.data.datasets[0].label = `Average Efficiency (${mode}) [km/L]`;
  chart.data.datasets[0].data = getData(stats);
  chart.options = buildDashboardOptions(mode);
  chart.update();
}
