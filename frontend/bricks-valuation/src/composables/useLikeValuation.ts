/**
 * Composable for handling valuation like/unlike functionality
 * Manages optimistic updates, API communication, and error handling
 *
 * Usage:
 * ```typescript
 * const { isLiking, isLiked, currentLikesCount, toggleLike } = useLikeValuation(
 *   currentUserId,
 *   valuationAuthorId
 * );
 *
 * await toggleLike(valuationId);
 * ```
 */

import { ref, type Ref } from 'vue';
import apiClient from '@/config/axios';
import { env } from '@/config/env';
import type {
  LikeValuationRequest,
  LikeValuationResponse,
  UseLikeValuationResult,
} from '@/types/bricksets';

/**
 * Utility to check if error is Axios-like with response
 */
function isAxiosErrorLike(error: unknown): error is {
  response?: {
    status?: number;
    data?: unknown;
  };
} {
  return typeof error === 'object' && error !== null && 'response' in error;
}

/**
 * Composable hook for managing valuation like operations
 * Implements optimistic updates with automatic rollback on error
 *
 * @param currentUserId - ID of currently authenticated user (null if not authenticated)
 * @param valuationAuthorId - ID of the user who created the valuation
 * @returns Like operation state and methods
 */
export function useLikeValuation(
  currentUserId: number | null,
  valuationAuthorId: number
): UseLikeValuationResult {
  // State: Like interaction tracking
  const isLiking = ref<boolean>(false);
  const isLiked = ref<boolean>(false);
  const currentLikesCount = ref<number>(0);

  /**
   * Validates whether current user can like this valuation
   * Returns false if:
   * - User is not authenticated
   * - User is the author of the valuation
   */
  const validateCanLike = (): boolean => {
    // Must be authenticated
    if (currentUserId === null) {
      return false;
    }

    // Cannot like own valuation
    if (currentUserId === valuationAuthorId) {
      return false;
    }

    return true;
  };

  /**
   * Toggles like status for a valuation with optimistic update
   *
   * Flow:
   * 1. Validate user can like
   * 2. Store previous state for rollback
   * 3. Apply optimistic update (UI changes immediately)
   * 4. Send API request
   * 5. On success: keep optimistic state
   * 6. On error: rollback to previous state and throw error
   *
   * @param valuationId - ID of valuation to like
   * @throws Error with user-friendly message on failure
   */
  const toggleLike = async (valuationId: number): Promise<void> => {
    // Validation checks
    if (!validateCanLike()) {
      throw new Error('Nie możesz polajkować tej wyceny');
    }

    // Guard against duplicate requests
    if (isLiking.value) {
      throw new Error('Żądanie już w trakcie');
    }

    // Store previous state for rollback
    const previousLikeState = isLiked.value;
    const previousCount = currentLikesCount.value;

    try {
      isLiking.value = true;

      // Optimistic update: assume like will succeed
      isLiked.value = true;
      currentLikesCount.value += 1;

      // API call
      const endpoint = `/v${env.api.version}/valuations/${valuationId}/likes`;
      const payload: LikeValuationRequest = {};

      await apiClient.post<LikeValuationResponse>(endpoint, payload, {
        withCredentials: true,
      });

      // Success - optimistic state is preserved
      // Response contains: { valuation_id, user_id, created_at }
      return;
    } catch (err) {
      // Rollback optimistic update on error
      isLiked.value = previousLikeState;
      currentLikesCount.value = previousCount;

      // Parse error and provide user-friendly message
      if (isAxiosErrorLike(err)) {
        const status = err.response?.status;

        if (status === 403) {
          // User trying to like own valuation
          throw new Error('Nie możesz polajkować własnej wyceny');
        } else if (status === 409) {
          // Duplicate like attempt
          throw new Error('Już polajkowałeś tę wycenę');
        } else if (status === 404) {
          // Valuation not found (was deleted)
          throw new Error('Wycena nie istnieje');
        } else if (status === 401) {
          // Session expired or token invalid
          throw new Error('Sesja wygasła - zaloguj się ponownie');
        } else if (status && status >= 500) {
          // Server error
          throw new Error('Błąd serwera - spróbuj później');
        }
      }

      // Network or other error
      throw new Error('Błąd połączenia - spróbuj ponownie');
    } finally {
      isLiking.value = false;
    }
  };

  return {
    isLiking: isLiking as Readonly<Ref<boolean>>,
    isLiked: isLiked as Readonly<Ref<boolean>>,
    currentLikesCount: currentLikesCount as Readonly<Ref<number>>,
    toggleLike,
    validateCanLike,
  };
}
