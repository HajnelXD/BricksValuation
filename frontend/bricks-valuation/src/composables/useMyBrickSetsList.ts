/**
 * useMyBrickSetsList Composable
 * Manages user's own bricksets list with pagination and sorting
 * Endpoint: GET /api/v1/users/me/bricksets
 */

import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '@/config/axios';
import { env } from '@/config/env';
import { useI18n } from 'vue-i18n';
import type {
  OwnedBrickSetDTO,
  OwnedBrickSetViewModel,
  OwnedBrickSetListResponseDTO,
  MyBrickSetsFilters,
  SortOrderingValue,
  UseMyBrickSetsListReturn,
} from '@/types/bricksets';
import { isValidMyBrickSetsOrdering } from '@/types/bricksets';

interface AxiosErrorLike {
  response?: {
    status?: number;
    data?: unknown;
  };
}

function isAxiosErrorLike(error: unknown): error is AxiosErrorLike {
  return typeof error === 'object' && error !== null && 'response' in error;
}

/**
 * Map DTO to ViewModel with formatted labels
 */
function mapOwnedBrickSetDtoToViewModel(
  dto: OwnedBrickSetDTO,
  productionStatusLabel: Record<string, string>,
  completenessLabel: Record<string, string>
): OwnedBrickSetViewModel {
  return {
    id: dto.id,
    number: dto.number.toString().padStart(5, '0'),
    productionStatusLabel: productionStatusLabel[dto.production_status as string] || dto.production_status,
    completenessLabel: completenessLabel[dto.completeness as string] || dto.completeness,
    valuationsCount: dto.valuations_count,
    totalLikes: dto.total_likes,
    editable: dto.editable,
  };
}

/**
 * Validate page number
 */
function validatePage(page: unknown): number {
  const parsed = typeof page === 'string' ? parseInt(page, 10) : page;
  return typeof parsed === 'number' && parsed > 0 ? parsed : 1;
}

/**
 * Validate page size
 */
function validatePageSize(pageSize: unknown): number {
  const parsed = typeof pageSize === 'string' ? parseInt(pageSize, 10) : pageSize;
  const size = typeof parsed === 'number' && parsed > 0 ? parsed : 10;
  return Math.min(100, Math.max(1, size)); // Clamp to 1-100
}

/**
 * Composable for managing user's bricksets list
 */
export function useMyBrickSetsList(): UseMyBrickSetsListReturn {
  const route = useRoute();
  const router = useRouter();
  const { t } = useI18n();

  // State
  const bricksets = ref<OwnedBrickSetViewModel[]>([]);
  const totalCount = ref(0);
  const isLoading = ref(false);
  const error = ref<Error | null>(null);
  const abortController = ref<AbortController | null>(null);

  // Filters from query params
  const page = ref(validatePage(route.query.page));
  const pageSize = ref(validatePageSize(route.query.page_size || 10));
  const ordering = ref<SortOrderingValue>(
    isValidMyBrickSetsOrdering(route.query.ordering) ? (route.query.ordering as SortOrderingValue) : '-created_at'
  );

  // Computed filter state
  const filters = computed<MyBrickSetsFilters>(() => ({
    page: page.value,
    page_size: pageSize.value,
    ordering: ordering.value,
  }));

  // Computed pagination values
  const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value));
  const hasNextPage = computed(() => page.value < totalPages.value);
  const hasPreviousPage = computed(() => page.value > 1);

  /**
   * Fetch bricksets from API
   */
  async function fetchBrickSets() {
    // Cancel previous request
    if (abortController.value) {
      abortController.value.abort();
    }

    abortController.value = new AbortController();
    isLoading.value = true;
    error.value = null;

    try {
      const endpoint = `/v${env.api.version}/users/me/bricksets`;
      const response = await apiClient.get<OwnedBrickSetListResponseDTO>(endpoint, {
        params: {
          page: page.value,
          page_size: pageSize.value,
          ordering: ordering.value,
        },
        signal: abortController.value.signal,
      });

      if (response.status === 200 && response.data) {
        // Map DTO to ViewModel with i18n labels (evaluate at fetch time, not initialization)
        const productionStatusLabel = {
          ACTIVE: t('myBrickSets.productionStatus.active'),
          RETIRED: t('myBrickSets.productionStatus.retired'),
        };

        const completenessLabel = {
          COMPLETE: t('myBrickSets.completeness.complete'),
          INCOMPLETE: t('myBrickSets.completeness.incomplete'),
        };

        bricksets.value = response.data.results.map((dto) =>
          mapOwnedBrickSetDtoToViewModel(dto, productionStatusLabel, completenessLabel)
        );
        totalCount.value = response.data.count;
        error.value = null;
      }
    } catch (err: unknown) {
      // Ignore abort errors
      if (err instanceof DOMException && err.name === 'AbortError') {
        return;
      }

      if (isAxiosErrorLike(err)) {
        const status = err.response?.status;

        if (status === 401) {
          error.value = new Error('NOT_AUTHENTICATED');
          // Router guard akan obsługować redirect
        } else if (status === 400) {
          error.value = new Error('INVALID_PARAMS');
          // Reset to defaults
          page.value = 1;
          ordering.value = '-created_at';
        } else if (status === 500) {
          error.value = new Error('SERVER_ERROR');
        } else if (status) {
          error.value = new Error(`HTTP_${status}`);
        } else {
          error.value = new Error('NETWORK_ERROR');
        }
      } else {
        error.value = err instanceof Error ? err : new Error('UNKNOWN_ERROR');
      }

      bricksets.value = [];
      totalCount.value = 0;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Change current page
   */
  async function changePage(newPage: number) {
    if (newPage < 1 || newPage > totalPages.value) {
      return;
    }

    page.value = newPage;
    await updateRouteAndFetch();
  }

  /**
   * Change sorting
   */
  async function changeSorting(newOrdering: SortOrderingValue) {
    if (!isValidMyBrickSetsOrdering(newOrdering)) {
      return;
    }

    ordering.value = newOrdering;
    page.value = 1; // Reset to first page on sort change
    await updateRouteAndFetch();
  }

  /**
   * Refresh list with current filters
   */
  async function refreshList() {
    await fetchBrickSets();
  }

  /**
   * Update router query params and fetch
   */
  async function updateRouteAndFetch() {
    const query: Record<string, string | number | undefined> = {
      page: page.value !== 1 ? page.value : undefined,
      page_size: pageSize.value !== 10 ? pageSize.value : undefined,
      ordering: ordering.value !== '-created_at' ? ordering.value : undefined,
    };

    // Clean up undefined values
    Object.keys(query).forEach((key) => {
      if (query[key] === undefined) {
        delete query[key];
      }
    });

    // Use replace to avoid history pollution
    await router.replace({
      query,
    });

    // Fetch is triggered by watcher
  }

  /**
   * Watcher on route query params
   */
  watch(
    () => route.query,
    () => {
      const newPage = validatePage(route.query.page);
      const newPageSize = validatePageSize(route.query.page_size);
      const newOrdering = isValidMyBrickSetsOrdering(route.query.ordering)
        ? (route.query.ordering as SortOrderingValue)
        : '-created_at';

      // Update state if changed
      if (newPage !== page.value || newPageSize !== pageSize.value || newOrdering !== ordering.value) {
        page.value = newPage;
        pageSize.value = newPageSize;
        ordering.value = newOrdering;
      }
    }
  );

  /**
   * Watcher on filter state to fetch when they change
   */
  watch(
    () => [page.value, pageSize.value, ordering.value],
    async () => {
      await fetchBrickSets();
    },
    { immediate: false } // Don't fetch immediately, onMounted will do it
  );

  /**
   * Fetch on component mount
   */
  onMounted(async () => {
    // Re-validate from route query params
    const newPage = validatePage(route.query.page);
    const newPageSize = validatePageSize(route.query.page_size);
    const newOrdering = isValidMyBrickSetsOrdering(route.query.ordering)
      ? (route.query.ordering as SortOrderingValue)
      : '-created_at';

    page.value = newPage;
    pageSize.value = newPageSize;
    ordering.value = newOrdering;

    await fetchBrickSets();
  });

  /**
   * Cleanup on unmount
   */
  onBeforeUnmount(() => {
    if (abortController.value) {
      abortController.value.abort();
    }
  });

  return {
    bricksets,
    totalCount,
    isLoading,
    error,
    filters,
    totalPages,
    hasNextPage,
    hasPreviousPage,
    fetchBrickSets,
    changePage,
    changeSorting,
    refreshList,
  };
}
