// ui/src/composables/useEntries.ts
import { computed, Ref, isRef, ref } from 'vue';
import type { FuelEntryDB } from '../types/FuelEntry';
import { compareEntries } from '../utils/compare';

/**
 * Sort fields supported by the comparator
 */
export type SortField =
  | 'date'
  | 'distance'
  | 'liters'
  | 'price_per_liter'
  | 'total_cost'
  | 'km_per_liter';

/**
 * Sort order supported by the comparator
 * - 'newest': descending order (latest first)
 * - 'oldest': ascending order (earliest first)
 */
export type SortOrder = 'newest' | 'oldest';

/**
 * Composable for filtering, sorting, and paginating fuel entries.
 *
 * @param entries - Array or Ref of FuelEntryDB items
 * @param sortField - Reactive sort field
 * @param sortOrder - Reactive sort order
 * @param filterText - Reactive filter string (matches notes text)
 * @param pageSize - Number of entries per page (default: 5)
 * @param currentPage - Reactive current page (default: 1)
 *
 * @returns filteredEntries, sortedEntries, visibleEntries, currentPage, totalPages
 */
export function useEntries(
  entries: FuelEntryDB[] | Ref<FuelEntryDB[]>,   // accepts both array and Ref
  sortField: Ref<SortField>,
  sortOrder: Ref<SortOrder>,
  filterText: Ref<string>,
  pageSize = 5,
  currentPage: Ref<number> = ref(1)              // optional pagination
) {
  // Normalize to a Ref so downstream code is consistent
  const source: Ref<FuelEntryDB[]> = isRef(entries) ? entries : ref(entries);

  /**
   * Filter entries by notes text
   */
  const filteredEntries = computed<FuelEntryDB[]>(() =>
    filterText.value
      ? source.value.filter((e) =>
          e.notes?.toLowerCase().includes(filterText.value.toLowerCase())
        )
      : source.value
  );

  /**
   * Sort entries using centralized comparator
   */
  const sortedEntries = computed<FuelEntryDB[]>(() => {
    const list = [...filteredEntries.value];
    list.sort((a, b) => compareEntries(a, b, sortField.value, sortOrder.value));
    return list;
  });

  /**
   * Total pages for pagination
   */
  const totalPages = computed(() =>
    Math.max(1, Math.ceil(sortedEntries.value.length / pageSize))
  );

  /**
   * Clamp currentPage to valid range
   */
  const clampedPage = computed(() =>
    Math.min(Math.max(currentPage.value, 1), totalPages.value)
  );

  /**
   * Paginate visible entries
   */
  const visibleEntries = computed<FuelEntryDB[]>(() => {
    const start = (clampedPage.value - 1) * pageSize;
    return sortedEntries.value.slice(start, start + pageSize);
  });

  return {
    filteredEntries,
    sortedEntries,
    visibleEntries,
    currentPage,
    totalPages,
  };
}
