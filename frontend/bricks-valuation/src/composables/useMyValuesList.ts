/**
 * useMyValuesList Composable
 * Manages user's own valuations list state, pagination, and API integration
 *
 * Features:
 * - Reactive state for valuations list and pagination
 * - Automatic data fetching on composable initialization
 * - Pagination support with page navigation
 * - Error handling (network, validation, auth)
 * - DTO to ViewModel mapping
 */

import { ref, computed, readonly } from 'vue';
import apiClient from '@/config/axios';
import { env } from '@/config/env';
import type {
  OwnedValuationListResponseDTO,
  OwnValuationViewModel,
  PaginationState,
} from '@/types/bricksets';
import { mapOwnedValuationDtoToViewModel } from '@/mappers/bricksets';

const API_BASE_URL = `/v${env.api.version}/users/me/valuations`;
const DEFAULT_PAGE_SIZE = 20;

interface AxiosErrorLike {
  response?: {
    status?: number;
    data?: unknown;
  };
  message?: string;
}

function isAxiosErrorLike(error: unknown): error is AxiosErrorLike {
  return typeof error === 'object' && error !== null;
}

/**
 * Create default pagination state
 */
function createDefaultPaginationState(): PaginationState {
  return {
    currentPage: 1,
    pageSize: DEFAULT_PAGE_SIZE,
    totalCount: 0,
    totalPages: 0,
    hasNextPage: false,
    hasPreviousPage: false,
  };
}

/**
 * Calculate pagination state from API response
 */
function calculatePaginationState(
  currentPage: number,
  pageSize: number,
  totalCount: number
): PaginationState {
  const totalPages = Math.ceil(totalCount / pageSize);
  return {
    currentPage,
    pageSize,
    totalCount,
    totalPages,
    hasNextPage: currentPage < totalPages,
    hasPreviousPage: currentPage > 1,
  };
}

/**
 * Create user-friendly error message based on error type
 */
function getUserFriendlyErrorMessage(error: unknown): string {
  if (isAxiosErrorLike(error)) {
    const status = error.response?.status;
    const message = error.message || '';

    if (status === 401) {
      return 'Sesja wygasła. Zaloguj się ponownie.';
    }
    if (status === 400) {
      return 'Błąd validacji parametrów paginacji.';
    }
    if (status === 500) {
      return 'Błąd serwera. Spróbuj później.';
    }
    if (message.toLowerCase().includes('timeout')) {
      return 'Żądanie przekroczyło limit czasu. Spróbuj ponownie.';
    }
    if (message.toLowerCase().includes('network')) {
      return 'Brak połączenia z serwerem. Sprawdź internet.';
    }
  }

  return 'Nie udało się załadować wycen. Spróbuj ponownie.';
}

/**
 * Main composable for managing user's valuations list
 */
export function useMyValuesList() {
  // State
  const valuations = ref<OwnValuationViewModel[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const pagination = ref<PaginationState>(createDefaultPaginationState());

  // Computed
  const isEmpty = computed(() => valuations.value.length === 0);
  const totalPages = computed(() => pagination.value.totalPages);
  const currentPage = computed(() => pagination.value.currentPage);

  /**
   * Fetch valuations from API for given page
   */
  async function fetchValuesList(page: number): Promise<void> {
    // Validate page number
    if (page < 1) {
      page = 1;
    }

    loading.value = true;
    error.value = null;

    try {
      const response = await apiClient.get<OwnedValuationListResponseDTO>(API_BASE_URL, {
        params: {
          page,
          page_size: DEFAULT_PAGE_SIZE,
        },
        withCredentials: true,
      });

      // Validate response structure
      if (
        !response.data ||
        typeof response.data.count !== 'number' ||
        !Array.isArray(response.data.results)
      ) {
        throw new Error('Invalid API response structure');
      }

      // Map DTOs to ViewModels
      valuations.value = response.data.results.map(mapOwnedValuationDtoToViewModel);

      // Update pagination state
      pagination.value = calculatePaginationState(page, DEFAULT_PAGE_SIZE, response.data.count);
    } catch (err) {
      error.value = getUserFriendlyErrorMessage(err);
      valuations.value = [];
      pagination.value = createDefaultPaginationState();
      console.error('Error fetching valuations:', err);
    } finally {
      loading.value = false;
    }
  }

  /**
   * Navigate to specific page
   */
  async function goToPage(pageNumber: number): Promise<void> {
    await fetchValuesList(pageNumber);
  }

  /**
   * Refresh current page data
   */
  async function refresh(): Promise<void> {
    await fetchValuesList(pagination.value.currentPage);
  }

  // Initial fetch on composable creation
  fetchValuesList(1);

  return {
    // State (readonly)
    valuations: readonly(valuations),
    loading: readonly(loading),
    error: readonly(error),
    pagination: readonly(pagination),

    // Computed
    isEmpty,
    totalPages,
    currentPage,

    // Methods
    fetchValuesList,
    goToPage,
    refresh,
  };
}
