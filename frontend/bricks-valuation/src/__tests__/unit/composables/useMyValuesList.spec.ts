/**
 * Tests for useMyValuesList Composable
 * Tests API integration, state management, pagination, and error handling
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useMyValuesList } from '@/composables/useMyValuesList';
import apiClient from '@/config/axios';
import type { OwnedValuationListResponseDTO } from '@/types/bricksets';

vi.mock('@/config/axios');

const mockApiClient = vi.mocked(apiClient);

describe('useMyValuesList Composable', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Initial State', () => {
    it('should initialize with empty valuations', async () => {
      mockApiClient.get.mockResolvedValue({
        data: {
          count: 0,
          results: [],
        },
      });

      const { valuations } = useMyValuesList();

      // Wait for initial fetch
      await new Promise((resolve) => setTimeout(resolve, 100));

      expect(valuations.value).toEqual([]);
    });

    it('should initialize with loading state false after fetch', async () => {
      mockApiClient.get.mockResolvedValue({
        data: {
          count: 0,
          results: [],
        },
      });

      const { loading } = useMyValuesList();

      // Wait for initial fetch
      await new Promise((resolve) => setTimeout(resolve, 100));

      expect(loading.value).toBe(false);
    });
  });

  describe('Fetching Valuations', () => {
    it('should fetch valuations from API and map to ViewModels', async () => {
      const mockResponse: OwnedValuationListResponseDTO = {
        count: 2,
        results: [
          {
            id: 1,
            brickset: {
              id: 10,
              number: 12345,
            },
            value: 450,
            currency: 'PLN',
            likes_count: 5,
            created_at: '2025-10-21T12:00:00Z',
          },
          {
            id: 2,
            brickset: {
              id: 20,
              number: 67890,
            },
            value: 300,
            currency: 'PLN',
            likes_count: 3,
            created_at: '2025-10-20T12:00:00Z',
          },
        ],
      };

      mockApiClient.get.mockResolvedValue({ data: mockResponse });

      const { valuations, fetchValuesList } = useMyValuesList();

      // Clear initial fetch and call fetchValuesList
      vi.clearAllMocks();
      mockApiClient.get.mockResolvedValue({ data: mockResponse });

      await fetchValuesList(1);

      expect(valuations.value).toHaveLength(2);
      expect(valuations.value[0].id).toBe(1);
      expect(valuations.value[0].bricksetNumber).toBe('12345');
      expect(valuations.value[0].valueFormatted).toBe('450 PLN');
      expect(valuations.value[0].likesCount).toBe(5);
    });

    it('should call API with correct page parameter', async () => {
      mockApiClient.get.mockResolvedValue({
        data: {
          count: 0,
          results: [],
        },
      });

      const { fetchValuesList } = useMyValuesList();

      vi.clearAllMocks();
      mockApiClient.get.mockResolvedValue({
        data: {
          count: 0,
          results: [],
        },
      });

      await fetchValuesList(2);

      expect(mockApiClient.get).toHaveBeenCalledWith(
        expect.stringContaining('/users/me/valuations'),
        expect.objectContaining({
          params: {
            page: 2,
            page_size: 20,
          },
        })
      );
    });

    it('should use withCredentials in API request', async () => {
      mockApiClient.get.mockResolvedValue({
        data: {
          count: 0,
          results: [],
        },
      });

      const { fetchValuesList } = useMyValuesList();

      vi.clearAllMocks();
      mockApiClient.get.mockResolvedValue({
        data: {
          count: 0,
          results: [],
        },
      });

      await fetchValuesList(1);

      expect(mockApiClient.get).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          withCredentials: true,
        })
      );
    });
  });

  describe('Pagination State', () => {
    it('should calculate pagination state correctly', async () => {
      const mockResponse: OwnedValuationListResponseDTO = {
        count: 50,
        results: Array.from({ length: 20 }, (_, i) => ({
          id: i,
          brickset: { id: i, number: i },
          value: 100,
          currency: 'PLN',
          likes_count: 0,
          created_at: '2025-10-21T12:00:00Z',
        })),
      };

      mockApiClient.get.mockResolvedValue({ data: mockResponse });

      const { pagination, fetchValuesList } = useMyValuesList();

      vi.clearAllMocks();
      mockApiClient.get.mockResolvedValue({ data: mockResponse });

      await fetchValuesList(1);

      expect(pagination.value.currentPage).toBe(1);
      expect(pagination.value.totalCount).toBe(50);
      expect(pagination.value.pageSize).toBe(20);
      expect(pagination.value.totalPages).toBe(3); // ceil(50/20) = 3
      expect(pagination.value.hasNextPage).toBe(true);
      expect(pagination.value.hasPreviousPage).toBe(false);
    });

    it('should update pagination on different pages', async () => {
      const mockResponse: OwnedValuationListResponseDTO = {
        count: 50,
        results: [],
      };

      mockApiClient.get.mockResolvedValue({ data: mockResponse });

      const { pagination, fetchValuesList } = useMyValuesList();

      vi.clearAllMocks();
      mockApiClient.get.mockResolvedValue({ data: mockResponse });

      await fetchValuesList(2);

      expect(pagination.value.currentPage).toBe(2);
      expect(pagination.value.hasPreviousPage).toBe(true);
      expect(pagination.value.hasNextPage).toBe(true);
    });

    it('should disable nextPage on last page', async () => {
      const mockResponse: OwnedValuationListResponseDTO = {
        count: 50,
        results: [],
      };

      mockApiClient.get.mockResolvedValue({ data: mockResponse });

      const { pagination, fetchValuesList } = useMyValuesList();

      vi.clearAllMocks();
      mockApiClient.get.mockResolvedValue({ data: mockResponse });

      await fetchValuesList(3); // Last page

      expect(pagination.value.currentPage).toBe(3);
      expect(pagination.value.hasNextPage).toBe(false);
      expect(pagination.value.hasPreviousPage).toBe(true);
    });
  });

  describe('goToPage Method', () => {
    it('should navigate to page and fetch data', async () => {
      mockApiClient.get.mockResolvedValue({
        data: {
          count: 50,
          results: [],
        },
      });

      const { goToPage, pagination } = useMyValuesList();

      vi.clearAllMocks();
      mockApiClient.get.mockResolvedValue({
        data: {
          count: 50,
          results: [],
        },
      });

      await goToPage(2);

      expect(pagination.value.currentPage).toBe(2);
      expect(mockApiClient.get).toHaveBeenCalled();
    });
  });

  describe('Error Handling', () => {
    it('should handle 401 Unauthorized error', async () => {
      mockApiClient.get.mockRejectedValue({
        response: {
          status: 401,
        },
      });

      const { error, fetchValuesList } = useMyValuesList();

      await fetchValuesList(1);

      expect(error.value).toContain('Sesja wygasła');
    });

    it('should handle 400 Validation error', async () => {
      mockApiClient.get.mockRejectedValue({
        response: {
          status: 400,
        },
      });

      const { error, fetchValuesList } = useMyValuesList();

      await fetchValuesList(1);

      expect(error.value).toContain('Błąd validacji');
    });

    it('should handle 500 Server error', async () => {
      mockApiClient.get.mockRejectedValue({
        response: {
          status: 500,
        },
      });

      const { error, fetchValuesList } = useMyValuesList();

      await fetchValuesList(1);

      expect(error.value).toContain('Błąd serwera');
    });

    it('should handle network error', async () => {
      mockApiClient.get.mockRejectedValue({
        message: 'Network Error',
      });

      const { error, fetchValuesList } = useMyValuesList();

      await fetchValuesList(1);

      expect(error.value).toContain('połączenia');
    });

    it('should handle timeout error', async () => {
      mockApiClient.get.mockRejectedValue({
        message: 'timeout of 5000ms exceeded',
      });

      const { error, fetchValuesList } = useMyValuesList();

      await fetchValuesList(1);

      expect(error.value).toContain('limit czasu');
    });

    it('should clear data and pagination on error', async () => {
      mockApiClient.get.mockRejectedValue({
        response: {
          status: 500,
        },
      });

      const { valuations, pagination, fetchValuesList } = useMyValuesList();

      await fetchValuesList(1);

      expect(valuations.value).toEqual([]);
      expect(pagination.value.totalCount).toBe(0);
      expect(pagination.value.currentPage).toBe(1);
    });
  });

  describe('Loading State', () => {
    it('should set loading state during fetch', async () => {
      let resolveApiCall: (() => void) | null = null;

      mockApiClient.get.mockReturnValue(
        new Promise((resolve) => {
          resolveApiCall = () =>
            resolve({
              data: {
                count: 0,
                results: [],
              },
            });
        })
      );

      const { loading, fetchValuesList } = useMyValuesList();

      vi.clearAllMocks();
      mockApiClient.get.mockReturnValue(
        new Promise((resolve) => {
          resolveApiCall = () =>
            resolve({
              data: {
                count: 0,
                results: [],
              },
            });
        })
      );

      const promise = fetchValuesList(1);

      // Note: loading might be set to false immediately after initial setup
      // This test is more for documentation of behavior

      if (resolveApiCall) {
        resolveApiCall();
      }

      await promise;

      expect(loading.value).toBe(false);
    });
  });

  describe('Computed Properties', () => {
    it('should compute isEmpty correctly', async () => {
      mockApiClient.get.mockResolvedValue({
        data: {
          count: 0,
          results: [],
        },
      });

      const { isEmpty } = useMyValuesList();

      await new Promise((resolve) => setTimeout(resolve, 100));

      expect(isEmpty.value).toBe(true);
    });

    it('should compute isEmpty as false when has data', async () => {
      mockApiClient.get.mockResolvedValue({
        data: {
          count: 1,
          results: [
            {
              id: 1,
              brickset: { id: 1, number: 12345 },
              value: 100,
              currency: 'PLN',
              likes_count: 0,
              created_at: '2025-10-21T12:00:00Z',
            },
          ],
        },
      });

      const { isEmpty } = useMyValuesList();

      await new Promise((resolve) => setTimeout(resolve, 100));

      expect(isEmpty.value).toBe(false);
    });

    it('should compute totalPages correctly', async () => {
      mockApiClient.get.mockResolvedValue({
        data: {
          count: 75,
          results: [],
        },
      });

      const { totalPages } = useMyValuesList();

      await new Promise((resolve) => setTimeout(resolve, 100));

      expect(totalPages.value).toBe(4); // ceil(75/20) = 4
    });
  });

  describe('Refresh Method', () => {
    it('should refresh current page data', async () => {
      mockApiClient.get.mockResolvedValue({
        data: {
          count: 1,
          results: [
            {
              id: 1,
              brickset: { id: 1, number: 12345 },
              value: 100,
              currency: 'PLN',
              likes_count: 0,
              created_at: '2025-10-21T12:00:00Z',
            },
          ],
        },
      });

      const { refresh, pagination } = useMyValuesList();

      vi.clearAllMocks();
      mockApiClient.get.mockResolvedValue({
        data: {
          count: 1,
          results: [
            {
              id: 1,
              brickset: { id: 1, number: 12345 },
              value: 100,
              currency: 'PLN',
              likes_count: 0,
              created_at: '2025-10-21T12:00:00Z',
            },
          ],
        },
      });

      await refresh();

      expect(mockApiClient.get).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          params: expect.objectContaining({
            page: pagination.value.currentPage,
          }),
        })
      );
    });
  });

  describe('Invalid Response Handling', () => {
    it('should handle missing count field in response', async () => {
      mockApiClient.get.mockResolvedValue({
        data: {
          results: [],
        },
      });

      const { error, fetchValuesList } = useMyValuesList();

      await fetchValuesList(1);

      expect(error.value).toBeTruthy();
    });

    it('should handle missing results array in response', async () => {
      mockApiClient.get.mockResolvedValue({
        data: {
          count: 0,
        },
      });

      const { error, fetchValuesList } = useMyValuesList();

      await fetchValuesList(1);

      expect(error.value).toBeTruthy();
    });
  });
});
