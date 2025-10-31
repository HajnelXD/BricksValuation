import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useBrickSetDetail } from '@/composables/useBrickSetDetail';
import axiosInstance from '@/config/axios';
import type { BrickSetDetailDTO } from '@/types/bricksets';

vi.mock('@/config/axios');

describe('useBrickSetDetail Composable', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  const createMockDetailDTO = (overrides: Partial<BrickSetDetailDTO> = {}): BrickSetDetailDTO => ({
    id: 1,
    number: 10331,
    production_status: 'ACTIVE',
    completeness: 'COMPLETE',
    has_instructions: true,
    has_box: true,
    is_factory_sealed: false,
    owner_initial_estimate: 500,
    owner_id: 1,
    valuations: [],
    valuations_count: 0,
    total_likes: 0,
    created_at: '2024-01-01T10:00:00Z',
    updated_at: '2024-01-01T10:00:00Z',
    ...overrides,
  });

  it('initializes with default values', () => {
    const composable = useBrickSetDetail();

    expect(composable.brickSet.value).toBeNull();
    expect(composable.loading.value).toBe(false);
    expect(composable.error.value).toBeNull();
  });

  it('fetches brickset details successfully', async () => {
    const mockDto = createMockDetailDTO();
    const mockResponse = {
      status: 200,
      data: mockDto,
    };

    vi.mocked(axiosInstance.get).mockResolvedValueOnce(mockResponse);

    const composable = useBrickSetDetail();
    await composable.fetchBrickSet(1);

    expect(composable.loading.value).toBe(false);
    expect(composable.error.value).toBeNull();
    expect(composable.brickSet.value).toBeDefined();
    expect(composable.brickSet.value?.id).toBe(1);
    expect(composable.brickSet.value?.number).toBe('10331');
    expect(axiosInstance.get).toHaveBeenCalledWith('/v1/bricksets/1');
  });

  it('fetches brickset with valuations', async () => {
    const mockDto = createMockDetailDTO({
      valuations: [
        {
          id: 1,
          user_id: 10,
          value: 450,
          currency: 'PLN',
          comment: 'Good price',
          likes_count: 10,
          created_at: '2024-01-01T10:00:00Z',
        },
        {
          id: 2,
          user_id: 11,
          value: 500,
          currency: 'PLN',
          comment: 'Great condition',
          likes_count: 15,
          created_at: '2024-01-02T10:00:00Z',
        },
      ],
      valuations_count: 2,
      total_likes: 25,
    });

    const mockResponse = {
      status: 200,
      data: mockDto,
    };

    vi.mocked(axiosInstance.get).mockResolvedValueOnce(mockResponse);

    const composable = useBrickSetDetail();
    await composable.fetchBrickSet(1);

    expect(composable.brickSet.value?.valuations).toHaveLength(2);
    expect(composable.brickSet.value?.valuationsCount).toBe(2);
    expect(composable.brickSet.value?.totalLikes).toBe(25);
    expect(composable.brickSet.value?.topValuation).toBeDefined();
    expect(composable.brickSet.value?.topValuation?.likesCount).toBe(15);
  });

  it('handles 404 error correctly', async () => {
    const mockError = {
      response: {
        status: 404,
      },
    };

    vi.mocked(axiosInstance.get).mockRejectedValueOnce(mockError);

    const composable = useBrickSetDetail();
    await composable.fetchBrickSet(999);

    expect(composable.loading.value).toBe(false);
    expect(composable.error.value).toBe('Nie znaleziono zestawu');
    expect(composable.brickSet.value).toBeNull();
  });

  it('handles 500 error correctly', async () => {
    const mockError = {
      response: {
        status: 500,
      },
    };

    vi.mocked(axiosInstance.get).mockRejectedValueOnce(mockError);

    const composable = useBrickSetDetail();
    await composable.fetchBrickSet(1);

    expect(composable.error.value).toBe('Błąd serwera – spróbuj później');
    expect(composable.brickSet.value).toBeNull();
  });

  it('handles network error correctly', async () => {
    const mockError = new Error('Network error');

    vi.mocked(axiosInstance.get).mockRejectedValueOnce(mockError);

    const composable = useBrickSetDetail();
    await composable.fetchBrickSet(1);

    expect(composable.error.value).toBe('Błąd połączenia – sprawdź swoją sieć');
    expect(composable.brickSet.value).toBeNull();
  });

  it('likes valuation successfully', async () => {
    const mockDto = createMockDetailDTO({
      valuations: [
        {
          id: 1,
          user_id: 10,
          value: 450,
          currency: 'PLN',
          comment: 'Good price',
          likes_count: 10,
          created_at: '2024-01-01T10:00:00Z',
        },
      ],
      valuations_count: 1,
      total_likes: 10,
    });

    const mockGetResponse = {
      status: 200,
      data: mockDto,
    };

    const mockPostResponse = {
      status: 200,
      data: { success: true },
    };

    vi.mocked(axiosInstance.get).mockResolvedValue(mockGetResponse);
    vi.mocked(axiosInstance.post).mockResolvedValueOnce(mockPostResponse);

    const composable = useBrickSetDetail();
    await composable.fetchBrickSet(1);

    await composable.likeValuation(1);

    expect(axiosInstance.post).toHaveBeenCalledWith(
      '/v1/bricksets/1/valuations/1/like',
      {},
      { withCredentials: true }
    );
    expect(axiosInstance.get).toHaveBeenCalledTimes(2); // Initial fetch + refresh after like
  });

  it('throws error when liking without loaded brickset', async () => {
    const composable = useBrickSetDetail();

    await expect(composable.likeValuation(1)).rejects.toThrow('BrickSet not loaded');
  });

  it('handles 401 error when liking valuation', async () => {
    const mockDto = createMockDetailDTO();
    const mockGetResponse = {
      status: 200,
      data: mockDto,
    };

    const mockError = {
      response: {
        status: 401,
      },
    };

    vi.mocked(axiosInstance.get).mockResolvedValueOnce(mockGetResponse);
    vi.mocked(axiosInstance.post).mockRejectedValueOnce(mockError);

    const composable = useBrickSetDetail();
    await composable.fetchBrickSet(1);

    await expect(composable.likeValuation(1)).rejects.toThrow(
      'Musisz być zalogowany, aby polajkować wycenę'
    );
  });

  it('handles 400 error when liking valuation', async () => {
    const mockDto = createMockDetailDTO();
    const mockGetResponse = {
      status: 200,
      data: mockDto,
    };

    const mockError = {
      response: {
        status: 400,
      },
    };

    vi.mocked(axiosInstance.get).mockResolvedValueOnce(mockGetResponse);
    vi.mocked(axiosInstance.post).mockRejectedValueOnce(mockError);

    const composable = useBrickSetDetail();
    await composable.fetchBrickSet(1);

    await expect(composable.likeValuation(1)).rejects.toThrow('Nie możesz polajkować tej wyceny');
  });

  it('handles 404 error when liking valuation', async () => {
    const mockDto = createMockDetailDTO();
    const mockGetResponse = {
      status: 200,
      data: mockDto,
    };

    const mockError = {
      response: {
        status: 404,
      },
    };

    vi.mocked(axiosInstance.get).mockResolvedValueOnce(mockGetResponse);
    vi.mocked(axiosInstance.post).mockRejectedValueOnce(mockError);

    const composable = useBrickSetDetail();
    await composable.fetchBrickSet(1);

    await expect(composable.likeValuation(1)).rejects.toThrow('Nie znaleziono wyceny');
  });

  it('sets loading state during fetch', async () => {
    const mockDto = createMockDetailDTO();
    const mockResponse = {
      status: 200,
      data: mockDto,
    };

    let loadingDuringFetch = false;

    vi.mocked(axiosInstance.get).mockImplementation(async () => {
      loadingDuringFetch = composable.loading.value;
      return mockResponse;
    });

    const composable = useBrickSetDetail();
    await composable.fetchBrickSet(1);

    expect(loadingDuringFetch).toBe(true);
    expect(composable.loading.value).toBe(false);
  });
});
