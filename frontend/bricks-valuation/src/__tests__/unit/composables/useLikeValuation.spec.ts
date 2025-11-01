import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useLikeValuation } from '@/composables/useLikeValuation';
import apiClient from '@/config/axios';

vi.mock('@/config/axios');

describe('useLikeValuation Composable', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Initialization', () => {
    it('initializes with correct default state', () => {
      const likeComposable = useLikeValuation(1, 2);

      expect(likeComposable.isLiking.value).toBe(false);
      expect(likeComposable.isLiked.value).toBe(false);
      expect(likeComposable.currentLikesCount.value).toBe(0);
    });
  });

  describe('validateCanLike', () => {
    it('returns false when user is not authenticated (currentUserId is null)', () => {
      const likeComposable = useLikeValuation(null, 2);

      expect(likeComposable.validateCanLike()).toBe(false);
    });

    it('returns false when user is the valuation author', () => {
      const likeComposable = useLikeValuation(1, 1);

      expect(likeComposable.validateCanLike()).toBe(false);
    });

    it('returns true when user is authenticated and not the author', () => {
      const likeComposable = useLikeValuation(1, 2);

      expect(likeComposable.validateCanLike()).toBe(true);
    });
  });

  describe('toggleLike', () => {
    it('throws error when user is not authenticated', async () => {
      const likeComposable = useLikeValuation(null, 2);

      await expect(likeComposable.toggleLike(1)).rejects.toThrow(
        'Nie możesz polajkować tej wyceny'
      );
    });

    it('throws error when user is the valuation author', async () => {
      const likeComposable = useLikeValuation(1, 1);

      await expect(likeComposable.toggleLike(1)).rejects.toThrow(
        'Nie możesz polajkować tej wyceny'
      );
    });

    it('applies optimistic update before API call', async () => {
      const likeComposable = useLikeValuation(1, 2);
      likeComposable.currentLikesCount.value = 5;

      const mockPost = vi.spyOn(apiClient, 'post').mockResolvedValue({
        data: {
          valuation_id: 1,
          user_id: 1,
          created_at: '2025-11-01T10:00:00Z',
        },
      });

      await likeComposable.toggleLike(1);

      // Optimistic update should have increased count
      expect(likeComposable.currentLikesCount.value).toBe(6);
      expect(likeComposable.isLiked.value).toBe(true);

      mockPost.mockRestore();
    });

    it('makes correct API call with proper endpoint', async () => {
      const likeComposable = useLikeValuation(1, 2);

      const mockPost = vi.spyOn(apiClient, 'post').mockResolvedValue({
        data: {
          valuation_id: 123,
          user_id: 1,
          created_at: '2025-11-01T10:00:00Z',
        },
      });

      await likeComposable.toggleLike(123);

      expect(mockPost).toHaveBeenCalledWith(
        '/v1/valuations/123/likes',
        {},
        {
          withCredentials: true,
        }
      );

      mockPost.mockRestore();
    });

    it('sets isLiking to false when request completes', async () => {
      const likeComposable = useLikeValuation(1, 2);

      const mockPost = vi.spyOn(apiClient, 'post').mockResolvedValue({
        data: {
          valuation_id: 1,
          user_id: 1,
          created_at: '2025-11-01T10:00:00Z',
        },
      });

      expect(likeComposable.isLiking.value).toBe(false);
      const promise = likeComposable.toggleLike(1);
      expect(likeComposable.isLiking.value).toBe(true);

      await promise;
      expect(likeComposable.isLiking.value).toBe(false);

      mockPost.mockRestore();
    });

    it('throws error "Już polajkowałeś tę wycenę" on 409 Conflict', async () => {
      const likeComposable = useLikeValuation(1, 2);
      likeComposable.currentLikesCount.value = 5;

      const mockPost = vi.spyOn(apiClient, 'post').mockRejectedValue({
        response: {
          status: 409,
          data: {
            detail: 'Like duplicate',
            code: 'LIKE_DUPLICATE',
          },
        },
      });

      await expect(likeComposable.toggleLike(1)).rejects.toThrow('Już polajkowałeś tę wycenę');

      // Should rollback optimistic update
      expect(likeComposable.currentLikesCount.value).toBe(5);
      expect(likeComposable.isLiked.value).toBe(false);

      mockPost.mockRestore();
    });

    it('throws error "Nie możesz polajkować własnej wyceny" on 403 Forbidden', async () => {
      const likeComposable = useLikeValuation(1, 2);

      const mockPost = vi.spyOn(apiClient, 'post').mockRejectedValue({
        response: {
          status: 403,
          data: {
            detail: 'Cannot like own valuation',
            code: 'LIKE_OWN_VALUATION_FORBIDDEN',
          },
        },
      });

      await expect(likeComposable.toggleLike(1)).rejects.toThrow(
        'Nie możesz polajkować własnej wyceny'
      );

      mockPost.mockRestore();
    });

    it('throws error "Wycena nie istnieje" on 404 Not Found', async () => {
      const likeComposable = useLikeValuation(1, 2);

      const mockPost = vi.spyOn(apiClient, 'post').mockRejectedValue({
        response: {
          status: 404,
          data: {
            detail: 'Valuation not found',
          },
        },
      });

      await expect(likeComposable.toggleLike(1)).rejects.toThrow('Wycena nie istnieje');

      mockPost.mockRestore();
    });

    it('throws error "Sesja wygasła - zaloguj się ponownie" on 401 Unauthorized', async () => {
      const likeComposable = useLikeValuation(1, 2);

      const mockPost = vi.spyOn(apiClient, 'post').mockRejectedValue({
        response: {
          status: 401,
          data: {
            detail: 'Unauthorized',
          },
        },
      });

      await expect(likeComposable.toggleLike(1)).rejects.toThrow(
        'Sesja wygasła - zaloguj się ponownie'
      );

      mockPost.mockRestore();
    });

    it('throws generic server error message on 5xx status', async () => {
      const likeComposable = useLikeValuation(1, 2);

      const mockPost = vi.spyOn(apiClient, 'post').mockRejectedValue({
        response: {
          status: 500,
          data: {
            detail: 'Internal Server Error',
          },
        },
      });

      await expect(likeComposable.toggleLike(1)).rejects.toThrow('Błąd serwera - spróbuj później');

      mockPost.mockRestore();
    });

    it('throws network error message on network failure', async () => {
      const likeComposable = useLikeValuation(1, 2);

      const mockPost = vi.spyOn(apiClient, 'post').mockRejectedValue(new Error('Network error'));

      await expect(likeComposable.toggleLike(1)).rejects.toThrow(
        'Błąd połączenia - spróbuj ponownie'
      );

      mockPost.mockRestore();
    });

    it('rolls back optimistic update on error', async () => {
      const likeComposable = useLikeValuation(1, 2);
      likeComposable.currentLikesCount.value = 5;
      likeComposable.isLiked.value = false;

      const mockPost = vi.spyOn(apiClient, 'post').mockRejectedValue({
        response: {
          status: 409,
        },
      });

      try {
        await likeComposable.toggleLike(1);
      } catch {
        // Expected to throw
      }

      // State should be rolled back to previous values
      expect(likeComposable.currentLikesCount.value).toBe(5);
      expect(likeComposable.isLiked.value).toBe(false);
      expect(likeComposable.isLiking.value).toBe(false);

      mockPost.mockRestore();
    });

    it('prevents duplicate requests while one is in progress', async () => {
      const likeComposable = useLikeValuation(1, 2);

      const mockPost = vi.spyOn(apiClient, 'post').mockImplementation(
        () =>
          new Promise((resolve) => {
            setTimeout(() => {
              resolve({
                data: {
                  valuation_id: 1,
                  user_id: 1,
                  created_at: '2025-11-01T10:00:00Z',
                },
              });
            }, 100);
          })
      );

      const firstPromise = likeComposable.toggleLike(1);

      // Try to make another request while first is in progress
      expect(likeComposable.isLiking.value).toBe(true);
      await expect(likeComposable.toggleLike(1)).rejects.toThrow('Żądanie już w trakcie');

      await firstPromise;

      mockPost.mockRestore();
    });
  });
});
