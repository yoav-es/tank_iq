// ui/src/composables/useStats.ts
import { computed, Ref } from 'vue';
import type { DetailedStats, FuelEntryDB } from '../types/FuelEntry';
import { useFuelStore } from '../stores/fuelStore';
import { formatCurrency } from '../utils/format';

/**
 * Provide insight into fuel efficiency compared to average.
 *
 * @param value - Current efficiency value
 * @param avg - Average efficiency value
 * @returns Textual insight string
 */
export function efficiencyInsight(value: number, avg: number): string {
  if (value > avg * 1.1) return 'fuel consumption was higher than usual';
  if (value < avg * 0.9) return 'fuel consumption was lower than usual';
  return 'fuel consumption was close to average';
}

/**
 * Provide insight into driving distance compared to average.
 *
 * @param distance - Current distance value
 * @param avg - Average distance value
 * @returns Textual insight string
 */
export function distanceInsight(distance: number, avg: number): string {
  if (distance > avg * 1.1) return 'you drove a lot more than usual';
  if (distance < avg * 0.9) return 'you drove less than you normally do';
  return 'your driving distance was typical';
}

/**
 * Build summary block for yearly or monthly view.
 *
 * @param viewMode - Reactive mode ('yearly' or 'monthly')
 * @param selectedYearRow - Reactive selected yearly stats row
 * @param selectedMonthRow - Reactive selected monthly stats row
 * @param currencyCode - Reactive currency code for formatting
 *
 * @returns summaryBlock - Computed summary object or null
 */
export function useSummaryBlock(
  viewMode: Ref<'yearly' | 'monthly'>,
  selectedYearRow: Ref<DetailedStats['yearly_stats'][0] | null>,
  selectedMonthRow: Ref<DetailedStats['monthly_stats'][0] | null>,
  currencyCode: Ref<string>
) {
  const store = useFuelStore();
  const detailedStats = computed<DetailedStats | null>(() => store.detailedStats ?? null);

  const summaryBlock = computed(() => {
    const ds = detailedStats.value;
    if (!ds) return null;

    // Yearly summary
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
        totalCost: formatCurrency(row.total_cost, currencyCode.value),
        efficiencyCompare: row.average_km_per_liter >= avgAllYears ? 'higher' : 'lower',
        costCompare: row.total_cost >= avgAllCost ? 'rose' : 'fell'
      };
    }

    // Monthly summary
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
        totalCost: formatCurrency(row.total_cost, currencyCode.value),
        efficiencyCompare: row.average_km_per_liter >= avgYearEff ? 'higher' : 'lower',
        costCompare: row.total_cost >= avgYearCost ? 'rose' : 'fell'
      };
    }

    return null;
  });

  return { summaryBlock };
}

/**
 * Build yearly and monthly labels from detailed stats.
 *
 * @param detailedStats - Reactive DetailedStats object
 * @returns yearlyLabels and monthlyLabels as computed arrays
 */
export function usePeriodLabels(detailedStats: Ref<DetailedStats | null>) {
  const yearlyLabels = computed(() =>
    detailedStats.value?.yearly_stats.map(y => y.period_label).reverse() ?? []
  );
  const monthlyLabels = computed(() =>
    detailedStats.value?.monthly_stats.map(m => m.period_label).reverse() ?? []
  );
  return { yearlyLabels, monthlyLabels };
}

/**
 * Compute header text showing first and last year in stats.
 *
 * @param detailedStats - Reactive DetailedStats object
 * @returns Header string with period range
 */
export function computeHeaderPeriodLabel(detailedStats: Ref<DetailedStats | null>): string {
  const ds = detailedStats.value;
  if (!ds) return 'Period: —';
  const firstYear = ds.yearly_stats[0]?.period_label ?? '—';
  const lastYear = ds.yearly_stats[ds.yearly_stats.length - 1]?.period_label ?? '—';
  return `Period: ${firstYear} – ${lastYear}`;
}

/**
 * Get entries for a given month key.
 *
 * @param entries - Array of FuelEntryDB items
 * @param monthKey - Month key string (e.g. "2025-11")
 * @returns Filtered and reversed entries for that month
 */
export function getEntriesForMonth(entries: FuelEntryDB[], monthKey: string): FuelEntryDB[] {
  return entries.filter(e => e.date?.startsWith(monthKey)).reverse();
}
