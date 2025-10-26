import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useBrickSetListSearch } from '@/composables/useBrickSetListSearch';
import axiosInstance from '@/config/axios';

vi.mock('@/config/axios');

describe('useBrickSetListSearch Composable', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('initializes with default values', () => {
    const composable = useBrickSetListSearch();

    expect(composable.items.value).toEqual([]);
    expect(composable.loading.value).toBe(false);
    expect(composable.error.value).toBeNull();
    expect(composable.count.value).toBe(0);
  });

  it('initializes with custom initial filters', () => {
    const initialFilters = {
      q: 'test',
      production_status: 'ACTIVE' as const,
      completeness: 'COMPLETE' as const,
      has_instructions: true,
      has_box: false,
      is_factory_sealed: null,
      ordering: 'created_at' as const,
      page: 1,
    };

    const composable = useBrickSetListSearch({ initialFilters });

    expect(composable.filters.value.q).toBe('test');
    expect(composable.filters.value.production_status).toBe('ACTIVE');
  });

  it('fetches bricksets on initialization', async () => {
    const mockResponse = {
      status: 200,
      data: {
        results: [{ id: 1, number: 10001 }],
        count: 1,
      },
    };

    vi.mocked(axiosInstance.get).mockResolvedValueOnce(mockResponse);

    const composable = useBrickSetListSearch();

    await composable.fetch();

    expect(composable.count.value).toBe(1);
  });

  it('updates filters via setFilters method', async () => {
    const composable = useBrickSetListSearch();

    composable.setFilters({
      production_status: 'ACTIVE',
      completeness: 'COMPLETE',
      has_instructions: true,
    });

    expect(composable.filters.value.production_status).toBe('ACTIVE');
    expect(composable.filters.value.completeness).toBe('COMPLETE');
    expect(composable.filters.value.has_instructions).toBe(true);
  });

  it('resets all filters', async () => {
    const mockResponse = {
      status: 200,
      data: {
        results: [],
        count: 0,
      },
    };

    vi.mocked(axiosInstance.get).mockResolvedValueOnce(mockResponse);

    const composable = useBrickSetListSearch({
      initialFilters: { q: 'test', production_status: 'ACTIVE' as const },
    });

    composable.resetFilters();

    expect(composable.filters.value.q).toBe('');
    expect(composable.filters.value.production_status).toBeNull();
  });

  it('handles API errors gracefully', async () => {
    const errorMessage = 'Network error';
    vi.mocked(axiosInstance.get).mockRejectedValueOnce(new Error(errorMessage));

    const composable = useBrickSetListSearch();

    await composable.fetch();

    expect(composable.error.value).toBeTruthy();
  });

  it('handles 500 server error', async () => {
    const mockError = {
      response: {
        status: 500,
        data: { detail: 'Server error' },
      },
    };

    vi.mocked(axiosInstance.get).mockRejectedValueOnce(mockError);

    const composable = useBrickSetListSearch();

    await composable.fetch();

    expect(composable.error.value).toContain('serwera');
  });

  it('handles 400 validation error', async () => {
    const mockError = {
      response: {
        status: 400,
        data: { code: 'VALIDATION_ERROR' },
      },
    };

    vi.mocked(axiosInstance.get).mockRejectedValueOnce(mockError);

    const composable = useBrickSetListSearch();

    await composable.fetch();

    expect(composable.error.value).toBeTruthy();
  });

  it('handles 401 unauthorized error', async () => {
    const mockError = {
      response: {
        status: 401,
        data: { detail: 'Unauthorized' },
      },
    };

    vi.mocked(axiosInstance.get).mockRejectedValueOnce(mockError);

    const composable = useBrickSetListSearch();

    await composable.fetch();

    expect(composable.error.value).toContain('wygasła');
  });

  it('exposes all required methods', () => {
    const composable = useBrickSetListSearch();

    expect(typeof composable.setFilters).toBe('function');
    expect(typeof composable.resetFilters).toBe('function');
    expect(typeof composable.fetch).toBe('function');
  });

  it('exposes all required reactive properties', () => {
    const composable = useBrickSetListSearch();

    expect(composable.items).toBeDefined();
    expect(composable.loading).toBeDefined();
    expect(composable.error).toBeDefined();
    expect(composable.count).toBeDefined();
    expect(composable.filters).toBeDefined();
  });

  it('handles response with data correctly', async () => {
    const mockResponse = {
      status: 200,
      data: {
        results: [
          {
            id: 1,
            number: 10001,
            production_status: 'ACTIVE',
            completeness: 'COMPLETE',
          },
        ],
        count: 50,
      },
    };

    vi.mocked(axiosInstance.get).mockResolvedValueOnce(mockResponse);

    const composable = useBrickSetListSearch();

    await composable.fetch();

    expect(composable.count.value).toBe(50);
    expect(composable.items.value.length).toBeGreaterThan(0);
  });

  it('clears error on successful fetch', async () => {
    const mockResponse = {
      status: 200,
      data: {
        results: [],
        count: 0,
      },
    };

    vi.mocked(axiosInstance.get).mockResolvedValueOnce(mockResponse);

    const composable = useBrickSetListSearch();

    await composable.fetch();

    expect(composable.error.value).toBeNull();
  });

  it('sets loading state during fetch', async () => {
    vi.mocked(axiosInstance.get).mockImplementation(
      () =>
        new Promise((resolve) => {
          setTimeout(() => {
            resolve({
              status: 200,
              data: { results: [], count: 0 },
            });
          }, 50);
        }),
    );

    const composable = useBrickSetListSearch();

    const fetchPromise = composable.fetch();
    expect(composable.loading.value).toBe(true);

    await fetchPromise;

    expect(composable.loading.value).toBe(false);
  });

  it('validates ordering option on filter set', () => {
    const composable = useBrickSetListSearch();

    composable.setFilters({ ordering: 'created_at' as const });

    expect(composable.filters.value.ordering).toBeDefined();
  });

  it('builds correct endpoint URL with version', async () => {
    vi.mocked(axiosInstance.get).mockResolvedValueOnce({
      status: 200,
      data: { results: [], count: 0 },
    });

    const composable = useBrickSetListSearch();

    await composable.fetch();

    expect(axiosInstance.get).toHaveBeenCalled();
    const call = vi.mocked(axiosInstance.get).mock.calls[0];
    expect(call[0]).toContain('/bricksets');
  });
});
