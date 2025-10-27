/**
 * useBrickSetListSearch Composable
 * Manages BrickSet list state, filtering, fetching, and debounced search
 */

import { ref, watch, computed, reactive } from 'vue';
import apiClient from '@/config/axios';
import { env } from '@/config/env';
import type {
  BrickSetListItemViewModel,
  BrickSetFiltersState,
  UseBrickSetListSearchResult,
} from '@/types/bricksets';
import { DEFAULT_FILTERS_STATE } from '@/types/bricksets';
import {
  mapBrickSetDtoToListItemViewModel,
  validateOrderingOption,
} from '@/mappers/bricksets';

interface UseBrickSetListSearchOptions {
  initialFilters?: Partial<BrickSetFiltersState>;
}

/**
 * Debounce helper for search field
 */
function useDebounceFn(fn: () => void, delay: number) {
  let timeoutId: ReturnType<typeof setTimeout> | null = null;

  return {
    run() {
      if (timeoutId) clearTimeout(timeoutId);
      timeoutId = setTimeout(fn, delay);
    },
    flush() {
      if (timeoutId) clearTimeout(timeoutId);
      fn();
    },
    cancel() {
      if (timeoutId) clearTimeout(timeoutId);
    },
  };
}

/**
 * Build query params object from filter state
 * Only includes non-null/non-default values to minimize URL clutter
 */
export function buildQueryParams(filters: BrickSetFiltersState): Record<string, string> {
  const params: Record<string, string> = {};

  if (filters.q) {
    params.q = filters.q;
  }

  if (filters.production_status) {
    params.production_status = filters.production_status;
  }

  if (filters.completeness) {
    params.completeness = filters.completeness;
  }

  if (filters.has_instructions === true) {
    params.has_instructions = 'true';
  }

  if (filters.has_box === true) {
    params.has_box = 'true';
  }

  if (filters.is_factory_sealed === true) {
    params.is_factory_sealed = 'true';
  }

  if (filters.ordering && filters.ordering !== '-created_at') {
    params.ordering = filters.ordering;
  }

  if (filters.page > 1) {
    params.page = String(filters.page);
  }

  return params;
}

/**
 * Composable hook for managing brickset list search, filtering and pagination
 * Handles API integration, state management, and debounced search
 */
export function useBrickSetListSearch(options: UseBrickSetListSearchOptions = {}): UseBrickSetListSearchResult {
  // State
  const items = ref<BrickSetListItemViewModel[]>([]);
  const count = ref(0);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const filters = reactive<BrickSetFiltersState>({
    ...DEFAULT_FILTERS_STATE,
    ...options.initialFilters,
  });

  // Validate filters on creation
  filters.ordering = validateOrderingOption(filters.ordering);
  if (filters.page < 1) filters.page = 1;

  // API call logic
  const abortController = ref<AbortController | null>(null);

  async function fetch() {
    // Cancel previous request if in flight
    if (abortController.value) {
      abortController.value.abort();
    }

    abortController.value = new AbortController();
    loading.value = true;
    error.value = null;
    console.log('[BrickSetListSearch] Fetching with filters:', filters);

    try {
      const queryParams = buildQueryParams(filters);
      const endpoint = `/${env.api.version}/bricksets`;
      console.log('[BrickSetListSearch] Request:', { endpoint, queryParams });
      
      const response = await apiClient.get(endpoint, {
        params: queryParams,
        signal: abortController.value.signal,
      });

      console.log('[BrickSetListSearch] Success:', response.status, response.data);
      if (response.status === 200) {
        items.value = response.data.results.map(mapBrickSetDtoToListItemViewModel);
        count.value = response.data.count;
        error.value = null;
      }
    } catch (err: any) {
      console.error('[BrickSetListSearch] Error:', err);
      
      // Don't set error for aborted requests (user navigated away)
      if (err.name === 'AbortError') {
        console.log('[BrickSetListSearch] Request aborted');
        return;
      }

      // Handle axios errors
      const errorStatus = err.response?.status;
      console.error('[BrickSetListSearch] Error status:', errorStatus, err.response?.data);
      
      if (errorStatus === 400) {
          // Validation error - attempt recovery by resetting ordering
        const hasOrderingError = err.response?.data?.code === 'VALIDATION_ERROR';
        if (hasOrderingError && filters.ordering !== '-created_at') {
          filters.ordering = '-created_at';
          // Retry with corrected ordering
          await fetch();
          return;
        }
        error.value = 'Nieprawidłowe parametry filtrów – przywrócono domyślne sortowanie';
      } else if (errorStatus === 401) {
        error.value = 'Sesja wygasła – zaloguj się ponownie';
      } else if (errorStatus === 500) {
        error.value = 'Błąd serwera – spróbuj później';
      } else if (errorStatus) {
        error.value = 'Błąd podczas ładowania zestawów';
      } else {
        error.value = 'Błąd połączenia – sprawdź swoją sieć';
      }

      items.value = [];
      count.value = 0;
    } finally {
      loading.value = false;
      console.log('[BrickSetListSearch] Loading state:', loading.value);
    }
  }

  // Debounce search with 300ms delay
  const debouncedFetch = useDebounceFn(() => {
    fetch();
  }, 300);

  // Watchers
  watch(
    () => [
      filters.production_status,
      filters.completeness,
      filters.has_instructions,
      filters.has_box,
      filters.is_factory_sealed,
      filters.ordering,
    ],
    () => {
      // Reset to page 1 when filters change (non-search filters)
      filters.page = 1;
      fetch();
    },
  );

  watch(
    () => filters.q,
    () => {
      // Debounce search
      filters.page = 1;
      debouncedFetch.run();
    },
  );

  watch(
    () => filters.page,
    () => {
      fetch();
    },
  );

  // Methods
  function setFilters(partial: Partial<BrickSetFiltersState>) {
    const validOrdering = partial.ordering ? validateOrderingOption(partial.ordering) : undefined;

    Object.assign(filters, {
      ...partial,
      ...(validOrdering !== undefined && { ordering: validOrdering }),
    });
  }

  function resetFilters() {
    const newFilters: BrickSetFiltersState = {
      ...DEFAULT_FILTERS_STATE,
    };

    Object.assign(filters, newFilters);
    debouncedFetch.flush();
    fetch();
  }

  return {
    items: computed(() => items.value),
    count: computed(() => count.value),
    loading: computed(() => loading.value),
    error: computed(() => error.value),
    filters: computed(() => ({ ...filters })),
    setFilters,
    resetFilters,
    fetch,
  };
}
