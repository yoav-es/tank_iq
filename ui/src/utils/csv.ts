// ui/src/utils/csv.ts
import type { FuelEntryInput, FuelEntryDB } from '../types/FuelEntry';

/**
 * Parse a single CSV row into fields, supporting quoted values and commas inside quotes.
 * - Fields may be wrapped in double quotes.
 * - Double quotes inside quoted fields are escaped by doubling them ("").
 */
function parseCsvRow(row: string): string[] {
  const fields: string[] = [];
  let current = '';
  let inQuotes = false;

  for (let i = 0; i < row.length; i++) {
    const char = row[i];

    if (inQuotes) {
      if (char === '"') {
        // Check for escaped quote
        if (row[i + 1] === '"') {
          current += '"';
          i++; // skip the escaped quote
        } else {
          inQuotes = false; // closing quote
        }
      } else {
        current += char;
      }
    } else {
      if (char === '"') {
        inQuotes = true;
      } else if (char === ',') {
        fields.push(current);
        current = '';
      } else {
        current += char;
      }
    }
  }
  fields.push(current);
  return fields;
}

/**
 * Parse CSV rows into FuelEntryInput objects.
 * Expects header row: date,distance,liters,price_per_liter,notes
 *
 * - Supports quoted notes containing commas and quotes.
 * - Filters out rows with missing date or non-numeric distance/liters/price_per_liter.
 *
 * @param rows - Array of CSV rows including a header
 * @returns Array of FuelEntryInput objects
 */
export function parseCsvRows(rows: string[]): FuelEntryInput[] {
  if (!rows.length) return [];

  // Optionally validate header (lenient: trims and lowercases)
  const header = rows[0].split(',').map((h) => h.trim().toLowerCase());
  const expected = ['date', 'distance', 'liters', 'price_per_liter', 'notes'];
  const headerValid =
    header.length >= expected.length &&
    expected.every((col, idx) => header[idx] === col);

  const dataRows = headerValid ? rows.slice(1) : rows;

  return dataRows
    .map((row) => {
      const fields = parseCsvRow(row);
      const [date, distance, liters, pricePerLiter, ...notesParts] = fields;
      const notesRaw = notesParts.length ? notesParts.join(',') : '';
      const entry: FuelEntryInput = {
        date: (date ?? '').trim(),
        distance: Number((distance ?? '').trim()),
        liters: Number((liters ?? '').trim()),
        price_per_liter: Number((pricePerLiter ?? '').trim()),
        notes: (notesRaw ?? '').trim(),
      };
      return entry;
    })
    .filter(
      (e) =>
        !!e.date &&
        !isNaN(e.distance) &&
        !isNaN(e.liters) &&
        !isNaN(e.price_per_liter)
    );
}

/**
 * Escape a CSV field according to RFC 4180-style rules:
 * - Wrap in double quotes if it contains a comma, quote, or newline.
 * - Escape internal quotes by doubling them.
 */
function escapeCsvField(value: string | number | null | undefined): string {
  const s = value == null ? '' : String(value);
  const needsQuoting = /[",\n]/.test(s);
  if (!needsQuoting) return s;
  return `"${s.replace(/"/g, '""')}"`;
}

/**
 * Convert entries to a CSV string.
 * Properly escapes fields that contain commas, quotes, or newlines.
 *
 * @param entries - Array of FuelEntryDB objects
 * @returns CSV string with header row
 */
export function toCsv(entries: FuelEntryDB[]): string {
  const header = 'date,distance,liters,price_per_liter,notes\n';
  const rows = entries.map((e) =>
    [
      escapeCsvField(e.date),
      escapeCsvField(e.distance),
      escapeCsvField(e.liters),
      escapeCsvField(e.price_per_liter),
      escapeCsvField(e.notes ?? ''),
    ].join(',')
  );
  return header + rows.join('\n');
}

/**
 * Trigger a CSV file download in the browser.
 *
 * @param csvText - CSV content as string
 * @param filename - Optional filename (default: fuel_log.csv)
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
