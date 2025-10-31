/**
 * useBrickSetEdit Composable
 * Manages BrickSet editing and deletion operations
 * Handles API calls for fetching, updating, and deleting BrickSets
 *
 * Client-side validation (RB-01):
 * - Calculates editable/deletable flags based on valuations and likes
 * - A BrickSet is editable/deletable if it has no valuations with likes
 */

import { ref, readonly, type Ref } from 'vue';
import apiClient from '@/config/axios';
import { env } from '@/config/env';
import type {
  BrickSetEditDetailDTO,
  BrickSetUpdateDTO,
  BrickSetDetailDTO,
} from '@/types/bricksets';

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
 * Calculate if a BrickSet can be edited (RB-01 business rule)
 * Frontend validation: editable if no valuations have likes
 * @param brickSet - The BrickSet to check
 * @returns true if editable, false otherwise
 */
function calculateEditable(brickSet: BrickSetDetailDTO): boolean {
  // RB-01: A BrickSet is editable if:
  // - No valuations exist with likes > 0
  // - In this simplified check, we use total_likes as a proxy
  // - If any valuation has likes, total_likes > 0, so not editable
  return brickSet.total_likes === 0;
}

export interface UseBrickSetEditResult {
  brickSet: Readonly<Ref<BrickSetEditDetailDTO | null>>;
  isLoading: Readonly<Ref<boolean>>;
  error: Readonly<Ref<string | null>>;
  fetchBrickSet: (id: number) => Promise<void>;
  updateBrickSet: (id: number, data: BrickSetUpdateDTO) => Promise<BrickSetEditDetailDTO>;
  deleteBrickSet: (id: number) => Promise<void>;
}

/**
 * Composable for managing BrickSet edit operations
 * Provides methods for fetching, updating, and deleting BrickSets
 */
export function useBrickSetEdit(): UseBrickSetEditResult {
  // State
  const brickSet = ref<BrickSetEditDetailDTO | null>(null);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  /**
   * Fetch BrickSet details with editable/deletable flags (client-side calculated)
   * @param id - BrickSet ID
   * @throws Error with specific error codes
   */
  async function fetchBrickSet(id: number): Promise<void> {
    isLoading.value = true;
    error.value = null;
    brickSet.value = null;

    try {
      const response = await apiClient.get<BrickSetDetailDTO>(
        `/v${env.api.version}/bricksets/${id}`
      );

      if (response.status === 200) {
        // Calculate editable/deletable flags based on RB-01 business rule
        const data = response.data;
        const editable = calculateEditable(data);

        // Add calculated flags to response
        const brickSetWithFlags: BrickSetEditDetailDTO = {
          ...data,
          editable,
          deletable: editable, // Both edit and delete use same RB-01 rule
        };

        brickSet.value = brickSetWithFlags;
        error.value = null;
      }
    } catch (err: unknown) {
      if (isAxiosErrorLike(err)) {
        const errorStatus = err.response?.status;

        if (errorStatus === 404) {
          error.value = 'BRICKSET_NOT_FOUND';
          throw new Error('BRICKSET_NOT_FOUND');
        } else if (errorStatus === 401) {
          error.value = 'NOT_AUTHENTICATED';
          throw new Error('NOT_AUTHENTICATED');
        } else if (errorStatus === 403) {
          error.value = 'FORBIDDEN';
          throw new Error('FORBIDDEN');
        } else {
          error.value = 'FETCH_FAILED';
          throw new Error('FETCH_FAILED');
        }
      } else {
        error.value = 'UNKNOWN_ERROR';
        throw new Error('UNKNOWN_ERROR');
      }
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Update BrickSet (partial update)
   * @param id - BrickSet ID
   * @param data - Partial update data
   * @returns Updated BrickSet with editable/deletable flags
   * @throws Error with specific error codes or validation errors
   */
  async function updateBrickSet(
    id: number,
    data: BrickSetUpdateDTO
  ): Promise<BrickSetEditDetailDTO> {
    try {
      const response = await apiClient.patch<BrickSetDetailDTO>(
        `/v${env.api.version}/bricksets/${id}`,
        data
      );

      if (response.status === 200) {
        // Calculate editable/deletable flags based on RB-01 business rule
        const responseData = response.data;
        const editable = calculateEditable(responseData);

        // Add calculated flags to response
        const brickSetWithFlags: BrickSetEditDetailDTO = {
          ...responseData,
          editable,
          deletable: editable,
        };

        brickSet.value = brickSetWithFlags;
        return brickSetWithFlags;
      }

      throw new Error('UPDATE_FAILED');
    } catch (err: unknown) {
      if (isAxiosErrorLike(err)) {
        const errorStatus = err.response?.status;

        if (errorStatus === 403) {
          const errorData = err.response?.data as { code?: string };
          throw new Error(errorData?.code || 'BRICKSET_EDIT_FORBIDDEN');
        } else if (errorStatus === 400) {
          // Validation error - throw the full error data
          throw {
            type: 'VALIDATION_ERROR',
            errors: err.response?.data,
          };
        } else if (errorStatus === 404) {
          throw new Error('BRICKSET_NOT_FOUND');
        } else if (errorStatus === 401) {
          throw new Error('NOT_AUTHENTICATED');
        } else {
          throw new Error('UPDATE_FAILED');
        }
      }

      throw new Error('UNKNOWN_ERROR');
    }
  }

  /**
   * Delete BrickSet
   * @param id - BrickSet ID
   * @throws Error with specific error codes
   */
  async function deleteBrickSet(id: number): Promise<void> {
    try {
      const response = await apiClient.delete(`/v${env.api.version}/bricksets/${id}`);

      if (response.status === 204 || response.status === 200) {
        brickSet.value = null;
        return;
      }

      throw new Error('DELETE_FAILED');
    } catch (err: unknown) {
      if (isAxiosErrorLike(err)) {
        const errorStatus = err.response?.status;

        if (errorStatus === 403) {
          throw new Error('BRICKSET_DELETE_FORBIDDEN');
        } else if (errorStatus === 404) {
          throw new Error('BRICKSET_NOT_FOUND');
        } else if (errorStatus === 401) {
          throw new Error('NOT_AUTHENTICATED');
        } else {
          throw new Error('DELETE_FAILED');
        }
      }

      throw new Error('UNKNOWN_ERROR');
    }
  }

  return {
    brickSet: readonly(brickSet),
    isLoading: readonly(isLoading),
    error: readonly(error),
    fetchBrickSet,
    updateBrickSet,
    deleteBrickSet,
  };
}
