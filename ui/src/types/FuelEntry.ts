// ui/src/types/fuelEntry.ts

/**
 * Base model shared across all fuel entry types.
 */
export interface FuelEntryBase {
  /** Date of entry in YYYY-MM-DD format (nullable) */
  date: string | null;
  /** Liters of fuel filled */
  liters: number;
  /** Price per liter of fuel */
  price_per_liter: number;
  /** Distance driven since last fill */
  distance: number;
  /** Optional notes for the entry */
  notes?: string | null;
}

/**
 * Input model used for creating or updating entries.
 * Direct alias of FuelEntryBase.
 */
export type FuelEntryInput = FuelEntryBase;

/**
 * Database/output model including calculated fields.
 */
export interface FuelEntryDB extends FuelEntryBase {
  /** Unique identifier */
  id: number;
  /** Total cost for this entry */
  total_cost: number;
  /** Efficiency in km per liter */
  km_per_liter: number;
}

/**
 * Aggregated overall statistics across all entries.
 */
export interface OverallStats {
  total_distance: number;
  total_liters: number;
  total_cost: number;
  entry_count: number;
  average_km_per_liter: number;
  average_cost_per_liter: number;
  best_month_efficiency: number;
  best_year_efficiency: number;
}

/**
 * Aggregated statistics for a specific time period (month or year).
 */
export interface TimePeriodStats {
  /** Label for the period (e.g., "2024-07" or "2023") */
  period_label: string;
  total_liters: number;
  total_cost: number;
  total_distance: number;
  count: number;
  average_km_per_liter: number;
  average_cost_per_liter: number;
}

/**
 * Detailed statistics response model (GET /stats/).
 */
export interface DetailedStats {
  overall_stats: OverallStats;
  monthly_stats: TimePeriodStats[];
  yearly_stats: TimePeriodStats[];
}

/**
 * List response model (GET /entries/).
 */
export interface EntryListResponse {
  entries: FuelEntryDB[];
  overall_stats: OverallStats;
}

/**
 * Factory function for creating a blank fuel entry.
 *
 * @returns FuelEntryInput with default values
 */
export function emptyEntry(): FuelEntryInput {
  return { date: '', distance: 0, liters: 0, price_per_liter: 0, notes: '' };
}
