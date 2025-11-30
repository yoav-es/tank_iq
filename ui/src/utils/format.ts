// ui/src/utils/format.ts

/**
 * Format a date string into DD/MM/YYYY format.
 * Example: "2025-11-28" → "28/11/2025"
 */
export function formatDate(dateStr?: string | null): string {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  if (isNaN(date.getTime())) return '';
  return date.toLocaleDateString('en-GB'); // en-GB gives DD/MM/YYYY
}

/**
 * Format a number with fixed decimals.
 */
export function formatNumber(value?: number | null, decimals = 2): string {
  if (value === null || value === undefined || isNaN(value)) return '';
  return value.toFixed(decimals);
}

/**
 * Format a number as currency.
 * Default: ILS (Israeli Shekel), locale defaults to he-IL.
 */
export function formatCurrency(
  value?: number | null,
  currency = 'ILS',
  locale = 'he-IL'
): string {
  if (value === null || value === undefined || isNaN(value)) return '';
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency,
  }).format(value);
}

/**
 * Format a percentage.
 */
export function formatPercentage(value?: number | null, decimals = 2): string {
  if (value === null || value === undefined || isNaN(value)) return '';
  return `${(value * 100).toFixed(decimals)}%`;
}

/**
 * Format distance in kilometers using Intl.NumberFormat.
 * Example: 1234.56 → "1,234.6 km"
 */
export function formatDistance(value?: number | null, decimals = 1, locale = 'en-GB'): string {
  if (value === null || value === undefined || isNaN(value)) return '';
  return new Intl.NumberFormat(locale, {
    style: 'unit',
    unit: 'kilometer',
    maximumFractionDigits: decimals,
  }).format(value);
}
