// ui/src/utils/compare.ts
import type { FuelEntryDB } from '../types/FuelEntry';

/**
 * Compare two fuel entries by a given field and order.
 *
 * @param a - First fuel entry
 * @param b - Second fuel entry
 * @param field - Field to compare (numeric fields or 'date')
 * @param order - Sort order ('newest' = descending, 'oldest' = ascending)
 * @returns Negative if a < b, positive if a > b, zero if equal
 */
export function compareEntries(
  a: FuelEntryDB,
  b: FuelEntryDB,
  field: keyof FuelEntryDB,
  order: 'newest' | 'oldest'
): number {
  if (field === 'date') {
    const da = a.date ? new Date(a.date).getTime() : 0;
    const db = b.date ? new Date(b.date).getTime() : 0;
    return order === 'newest' ? db - da : da - db;
  }

  // Only meaningful for numeric fields
  const av = typeof a[field] === 'number' ? (a[field] as number) : 0;
  const bv = typeof b[field] === 'number' ? (b[field] as number) : 0;

  return order === 'newest' ? bv - av : av - bv;
}
