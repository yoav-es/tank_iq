// ui/src/types/FuelEntry.ts

// The standard convention is to use 'interface' for object shapes.

// --- 1. Base Model (Shared Fields) ---
export interface FuelEntryBase {
  date: string; // YYYY-MM-DD format
  liters: number;
  price_per_liter: number;
  distance: number;
  notes?: string | null; // Optional fields are marked with '?'
}

// --- 2. Input/Create/Update Model ---
// Using a type alias here as it's a direct copy of FuelEntryBase.
export type FuelEntryInput = FuelEntryBase; 


// --- 3. Database/Output Model (Includes Calculated Fields) ---
// Extends the base interface.
export interface FuelEntryDB extends FuelEntryBase {
  id: number;
  total_cost: number;
  km_per_liter: number;
}


// --- 4. Overall Stats Model ---
export interface OverallStats {
  total_distance: number;
  total_liters: number;
  total_cost: number;
  entry_count: number;
  average_km_per_liter: number;
  average_cost_per_liter: number;
}


// --- 5. Time Period Stats Model (For Aggregation) ---
export interface TimePeriodStats {
  period_label: string; // e.g., "2024-07" or "2023"
  total_liters: number;
  total_cost: number;
  total_distance: number;
  count: number;
  average_km_per_liter: number;
  average_cost_per_liter: number;
}


// --- 6. Detailed Stats Response Model (GET /stats/) ---
export interface DetailedStats {
  overall_stats: OverallStats;
  monthly_stats: TimePeriodStats[];
  yearly_stats: TimePeriodStats[];
}


// --- 7. List Response Model (GET /entries/) ---
export interface EntryListResponse {
  entries: FuelEntryDB[];
  overall_stats: OverallStats;
}