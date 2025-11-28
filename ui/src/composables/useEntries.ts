// ui/src/composables/useEntries.ts
import { computed, Ref, isRef, ref } from 'vue';
import type { FuelEntryDB } from '../types/fuel-entry';
import { compareEntries } from '../utils/compare';

export function useEntries(
  entries: FuelEntryDB[] | Ref<FuelEntryDB[]>,   // accepts both array and Ref
  sortField: Ref<'date' | 'distance' | 'liters' | 'price_per_liter' | 'total_cost' | 'km_per_liter'>,
  sortOrder: Ref<'newest' | 'oldest'>,           // ✅ match comparator
  filterText: Ref<string>,
  pageSize = 5,
  currentPage: Ref<number> = ref(1)              // optional pagination
) {
  // Normalize to a Ref so downstream code is consistent
  const source = isRef(entries) ? entries : ref(entries);

  // Filter entries by notes text
  const filteredEntries = computed<FuelEntryDB[]>(() =>
    filterText.value
      ? source.value.filter((e) =>
          e.notes?.toLowerCase().includes(filterText.value.toLowerCase())
        )
      : source.value
  );

  // Sort entries using centralized comparator
  const sortedEntries = computed<FuelEntryDB[]>(() => {
    const list = [...filteredEntries.value];
    list.sort((a, b) => compareEntries(a, b, sortField.value, sortOrder.value));
    return list;
  });

  // Paginate visible entries
  const visibleEntries = computed<FuelEntryDB[]>(() => {
    const start = (currentPage.value - 1) * pageSize;
    return sortedEntries.value.slice(start, start + pageSize);
  });

  return {
    filteredEntries,
    sortedEntries,
    visibleEntries,
    currentPage,
  };
}
