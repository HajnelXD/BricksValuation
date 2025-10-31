/**
 * useBrickSetDetail Composable
 * Manages fetching and displaying detailed BrickSet data
 * Handles like operations for valuations
 */

import { ref, readonly } from 'vue';
import apiClient from '@/config/axios';
import { env } from '@/config/env';
import type { BrickSetDetailDTO, BrickSetDetailViewModel } from '@/types/bricksets';
import { mapBrickSetDetailDtoToViewModel } from '@/mappers/bricksets';

interface AxiosErrorLike {
  response?: {
    status?: number;
    data?: unknown;
  };
}

function isAxiosErrorLike(error: unknown): error is AxiosErrorLike {
  return typeof error === 'object' && error !== null && 'response' in error;
}

export interface UseBrickSetDetailResult {
  brickSet: Readonly<typeof brickSet>;
  loading: Readonly<typeof loading>;
  error: Readonly<typeof error>;
  fetchBrickSet: (id: number) => Promise<void>;
  likeValuation: (valuationId: number) => Promise<void>;
}

/**
 * Composable for managing BrickSet detail view
 * Fetches BrickSet details from API and provides like functionality
 */
export function useBrickSetDetail(): UseBrickSetDetailResult {
  // State
  const brickSet = ref<BrickSetDetailViewModel | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  /**
   * Fetch BrickSet details from API
   * @param id - BrickSet ID
   */
  async function fetchBrickSet(id: number): Promise<void> {
    loading.value = true;
    error.value = null;
    brickSet.value = null;

    try {
      const response = await apiClient.get<BrickSetDetailDTO>(
        `/v${env.api.version}/bricksets/${id}`
      );

      if (response.status === 200) {
        brickSet.value = mapBrickSetDetailDtoToViewModel(response.data);
        error.value = null;
      }
    } catch (err: unknown) {
      if (isAxiosErrorLike(err)) {
        const errorStatus = err.response?.status;

        if (errorStatus === 404) {
          error.value = 'Nie znaleziono zestawu';
        } else if (errorStatus === 401) {
          error.value = 'Sesja wygasła – zaloguj się ponownie';
        } else if (errorStatus === 500) {
          error.value = 'Błąd serwera – spróbuj później';
        } else if (errorStatus) {
          error.value = 'Błąd podczas ładowania zestawu';
        } else {
          error.value = 'Błąd połączenia – sprawdź swoją sieć';
        }
      } else {
        error.value = 'Błąd połączenia – sprawdź swoją sieć';
      }

      brickSet.value = null;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Like a valuation
   * Requires authentication
   * @param valuationId - Valuation ID to like
   * @throws Error if like operation fails
   */
  async function likeValuation(valuationId: number): Promise<void> {
    if (!brickSet.value) {
      throw new Error('BrickSet not loaded');
    }

    try {
      await apiClient.post(
        `/v${env.api.version}/bricksets/${brickSet.value.id}/valuations/${valuationId}/like`,
        {},
        { withCredentials: true }
      );

      // Refresh BrickSet data after successful like
      await fetchBrickSet(brickSet.value.id);
    } catch (err: unknown) {
      if (isAxiosErrorLike(err)) {
        const errorStatus = err.response?.status;

        if (errorStatus === 401) {
          throw new Error('Musisz być zalogowany, aby polajkować wycenę');
        } else if (errorStatus === 400) {
          throw new Error('Nie możesz polajkować tej wyceny');
        } else if (errorStatus === 404) {
          throw new Error('Nie znaleziono wyceny');
        } else if (errorStatus === 500) {
          throw new Error('Błąd serwera – spróbuj później');
        } else {
          throw new Error('Błąd podczas polajkowania wyceny');
        }
      } else {
        throw new Error('Błąd połączenia – sprawdź swoją sieć');
      }
    }
  }

  return {
    brickSet: readonly(brickSet),
    loading: readonly(loading),
    error: readonly(error),
    fetchBrickSet,
    likeValuation,
  };
}
