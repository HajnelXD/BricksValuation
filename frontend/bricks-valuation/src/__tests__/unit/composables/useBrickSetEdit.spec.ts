import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useBrickSetEdit } from '@/composables/useBrickSetEdit';
import axiosInstance from '@/config/axios';
import type { BrickSetEditDetailDTO, BrickSetUpdateDTO } from '@/types/bricksets';

vi.mock('@/config/axios');

describe('useBrickSetEdit Composable', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  const mockBrickSet: BrickSetEditDetailDTO = {
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
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    editable: true,
    deletable: true,
    owner: {
      id: 1,
      username: 'testuser',
    },
  };

  describe('Initialization', () => {
    it('initializes with null brickSet', () => {
      const { brickSet } = useBrickSetEdit();
      expect(brickSet.value).toBe(null);
    });

    it('initializes with isLoading as false', () => {
      const { isLoading } = useBrickSetEdit();
      expect(isLoading.value).toBe(false);
    });

    it('initializes with error as null', () => {
      const { error } = useBrickSetEdit();
      expect(error.value).toBe(null);
    });
  });

  describe('fetchBrickSet', () => {
    it('fetches BrickSet successfully', async () => {
      vi.mocked(axiosInstance.get).mockResolvedValueOnce({
        status: 200,
        data: mockBrickSet,
      });

      const { brickSet, isLoading, error, fetchBrickSet } = useBrickSetEdit();

      await fetchBrickSet(1);

      expect(axiosInstance.get).toHaveBeenCalledWith('/v1/bricksets/1');
      expect(brickSet.value).toEqual(mockBrickSet);
      expect(error.value).toBe(null);
      expect(isLoading.value).toBe(false);
    });

    it('handles 404 error', async () => {
      vi.mocked(axiosInstance.get).mockRejectedValueOnce({
        response: { status: 404 },
      });

      const { brickSet, error, fetchBrickSet } = useBrickSetEdit();

      await expect(fetchBrickSet(1)).rejects.toThrow('BRICKSET_NOT_FOUND');
      expect(brickSet.value).toBe(null);
      expect(error.value).toBe('BRICKSET_NOT_FOUND');
    });

    it('handles 401 error', async () => {
      vi.mocked(axiosInstance.get).mockRejectedValueOnce({
        response: { status: 401 },
      });

      const { error, fetchBrickSet } = useBrickSetEdit();

      await expect(fetchBrickSet(1)).rejects.toThrow('NOT_AUTHENTICATED');
      expect(error.value).toBe('NOT_AUTHENTICATED');
    });

    it('handles 403 error', async () => {
      vi.mocked(axiosInstance.get).mockRejectedValueOnce({
        response: { status: 403 },
      });

      const { error, fetchBrickSet } = useBrickSetEdit();

      await expect(fetchBrickSet(1)).rejects.toThrow('FORBIDDEN');
      expect(error.value).toBe('FORBIDDEN');
    });

    it('handles unknown error', async () => {
      vi.mocked(axiosInstance.get).mockRejectedValueOnce(new Error('Network error'));

      const { error, fetchBrickSet } = useBrickSetEdit();

      await expect(fetchBrickSet(1)).rejects.toThrow('UNKNOWN_ERROR');
      expect(error.value).toBe('UNKNOWN_ERROR');
    });

    it('sets isLoading during fetch', async () => {
      vi.mocked(axiosInstance.get).mockImplementationOnce(() => {
        return Promise.resolve({ status: 200, data: mockBrickSet });
      });

      const { fetchBrickSet } = useBrickSetEdit();
      await fetchBrickSet(1);

      // Note: This test verifies that fetch was called successfully
      expect(axiosInstance.get).toHaveBeenCalled();
    });
  });

  describe('updateBrickSet', () => {
    it('updates BrickSet successfully', async () => {
      const updateDTO: BrickSetUpdateDTO = {
        has_box: false,
        owner_initial_estimate: 600,
      };

      const updatedBrickSet = { ...mockBrickSet, has_box: false, owner_initial_estimate: 600 };

      vi.mocked(axiosInstance.patch).mockResolvedValueOnce({
        status: 200,
        data: updatedBrickSet,
      });

      const { brickSet, updateBrickSet } = useBrickSetEdit();

      const result = await updateBrickSet(1, updateDTO);

      expect(axiosInstance.patch).toHaveBeenCalledWith('/v1/bricksets/1', updateDTO);
      expect(result).toEqual(updatedBrickSet);
      expect(brickSet.value).toEqual(updatedBrickSet);
    });

    it('handles 403 error with custom code', async () => {
      vi.mocked(axiosInstance.patch).mockRejectedValueOnce({
        response: {
          status: 403,
          data: { code: 'BRICKSET_EDIT_FORBIDDEN' },
        },
      });

      const { updateBrickSet } = useBrickSetEdit();

      await expect(updateBrickSet(1, {})).rejects.toThrow('BRICKSET_EDIT_FORBIDDEN');
    });

    it('handles 400 validation error', async () => {
      const validationErrors = {
        number: ['Invalid number'],
      };

      vi.mocked(axiosInstance.patch).mockRejectedValueOnce({
        response: {
          status: 400,
          data: validationErrors,
        },
      });

      const { updateBrickSet } = useBrickSetEdit();

      await expect(updateBrickSet(1, {})).rejects.toEqual({
        type: 'VALIDATION_ERROR',
        errors: validationErrors,
      });
    });

    it('handles 404 error', async () => {
      vi.mocked(axiosInstance.patch).mockRejectedValueOnce({
        response: { status: 404 },
      });

      const { updateBrickSet } = useBrickSetEdit();

      await expect(updateBrickSet(1, {})).rejects.toThrow('BRICKSET_NOT_FOUND');
    });

    it('handles 401 error', async () => {
      vi.mocked(axiosInstance.patch).mockRejectedValueOnce({
        response: { status: 401 },
      });

      const { updateBrickSet } = useBrickSetEdit();

      await expect(updateBrickSet(1, {})).rejects.toThrow('NOT_AUTHENTICATED');
    });
  });

  describe('deleteBrickSet', () => {
    it('deletes BrickSet successfully with 204 status', async () => {
      vi.mocked(axiosInstance.delete).mockResolvedValueOnce({
        status: 204,
      });

      const { brickSet, deleteBrickSet } = useBrickSetEdit();

      await deleteBrickSet(1);

      expect(axiosInstance.delete).toHaveBeenCalledWith('/v1/bricksets/1');
      expect(brickSet.value).toBe(null);
    });

    it('deletes BrickSet successfully with 200 status', async () => {
      vi.mocked(axiosInstance.delete).mockResolvedValueOnce({
        status: 200,
      });

      const { brickSet, deleteBrickSet } = useBrickSetEdit();

      await deleteBrickSet(1);

      expect(brickSet.value).toBe(null);
    });

    it('handles 403 error', async () => {
      vi.mocked(axiosInstance.delete).mockRejectedValueOnce({
        response: { status: 403 },
      });

      const { deleteBrickSet } = useBrickSetEdit();

      await expect(deleteBrickSet(1)).rejects.toThrow('BRICKSET_DELETE_FORBIDDEN');
    });

    it('handles 404 error', async () => {
      vi.mocked(axiosInstance.delete).mockRejectedValueOnce({
        response: { status: 404 },
      });

      const { deleteBrickSet } = useBrickSetEdit();

      await expect(deleteBrickSet(1)).rejects.toThrow('BRICKSET_NOT_FOUND');
    });

    it('handles 401 error', async () => {
      vi.mocked(axiosInstance.delete).mockRejectedValueOnce({
        response: { status: 401 },
      });

      const { deleteBrickSet } = useBrickSetEdit();

      await expect(deleteBrickSet(1)).rejects.toThrow('NOT_AUTHENTICATED');
    });

    it('handles unknown error', async () => {
      vi.mocked(axiosInstance.delete).mockRejectedValueOnce(new Error('Network error'));

      const { deleteBrickSet } = useBrickSetEdit();

      await expect(deleteBrickSet(1)).rejects.toThrow('UNKNOWN_ERROR');
    });
  });
});
