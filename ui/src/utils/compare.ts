// ui/src/utils/compare.ts
import type { FuelEntryDB } from '../types/fuel-entry';

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
  const av = a[field] ?? 0;
  const bv = b[field] ?? 0;
  return order === 'newest'
    ? (bv as number) - (av as number)
    : (av as number) - (bv as number);
}
