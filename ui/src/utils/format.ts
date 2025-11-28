// ui/src/utils/format.ts

/**
 * Format a date string into a human-readable format.
 * Example: "2025-11-28" → "Nov 28, 2025"
 */
export function formatDate(dateStr?: string | null): string {
  return dateStr ? new Date(dateStr).toLocaleDateString() : '';
}

/**
 * Format a number with fixed decimals.
 * Example: 12.3456 → "12.35"
 */
export function formatNumber(value: number, decimals = 2): string {
  if (value === null || value === undefined || isNaN(value)) return '';
  return value.toFixed(decimals);
}

/**
 * Format a number as currency.
 * Example: 1234.5 → "$1,234.50"
 */
export function formatCurrency(
  value: number,
  currency = 'USD',
  locale?: string
): string {
  if (value === null || value === undefined || isNaN(value)) return '';
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency,
  }).format(value);
}

/**
 * Format a percentage.
 * Example: 0.1234 → "12.34%"
 */
export function formatPercentage(value: number, decimals = 2): string {
  if (value === null || value === undefined || isNaN(value)) return '';
  return `${(value * 100).toFixed(decimals)}%`;
}

/**
 * Format distance (kilometers).
 * Example: 1234.56 → "1,234.6 km"
 */
export function formatDistance(value: number, decimals = 1): string {
  if (value === null || value === undefined || isNaN(value)) return '';
  return `${value.toFixed(decimals)} km`;
}
