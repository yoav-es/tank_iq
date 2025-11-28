// ui/src/utils/csv.ts
import type { FuelEntryInput, FuelEntryDB } from '../types/fuel-entry';

/**
 * Parse CSV rows into FuelEntryInput objects.
 * Expects header row: date,distance,liters,price_per_liter,notes
 */
export function parseCsvRows(rows: string[]): FuelEntryInput[] {
  return rows
    .slice(1)
    .map((row) => {
      const [date, distance, liters, price_per_liter, ...notesParts] = row.split(',');
      const notes = notesParts.join(','); // allow commas in notes
      return {
        date: date?.trim() || '',
        distance: Number(distance) || 0,
        liters: Number(liters) || 0,
        price_per_liter: Number(price_per_liter) || 0,
        notes: notes?.trim() || '',
      };
    })
    .filter(
      (entry) =>
        entry.date &&
        !isNaN(entry.distance) &&
        !isNaN(entry.liters) &&
        !isNaN(entry.price_per_liter)
    );
}

/**
 * Convert entries to CSV string.
 */
export function toCsv(entries: FuelEntryDB[]): string {
  const header = 'date,distance,liters,price_per_liter,notes\n';
  const rows = entries.map(
    (e) =>
      `${e.date},${e.distance},${e.liters},${e.price_per_liter},${e.notes || ''}`
  );
  return header + rows.join('\n');
}

/**
 * Trigger a CSV file download in the browser.
 */
export function downloadCsv(csvText: string, filename = 'fuel_log.csv'): void {
  const blob = new Blob([csvText], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
