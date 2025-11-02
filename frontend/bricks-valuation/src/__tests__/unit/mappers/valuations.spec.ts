/**
 * Tests for Valuation Mappers
 */

import { describe, it, expect } from 'vitest';
import { mapOwnedValuationDtoToViewModel } from '@/mappers/bricksets';
import type { OwnedValuationListItemDTO } from '@/types/bricksets';

describe('Valuation Mappers', () => {
  describe('mapOwnedValuationDtoToViewModel', () => {
    it('should map DTO to ViewModel correctly', () => {
      const dto: OwnedValuationListItemDTO = {
        id: 1,
        brickset: {
          id: 10,
          number: 12345,
        },
        value: 450,
        currency: 'PLN',
        likes_count: 5,
        created_at: '2025-10-21T12:00:00Z',
      };

      const viewModel = mapOwnedValuationDtoToViewModel(dto);

      expect(viewModel.id).toBe(1);
      expect(viewModel.bricksetId).toBe(10);
      expect(viewModel.likesCount).toBe(5);
    });

    it('should format brickset number with leading zeros', () => {
      const dto: OwnedValuationListItemDTO = {
        id: 1,
        brickset: {
          id: 10,
          number: 123,
        },
        value: 450,
        currency: 'PLN',
        likes_count: 5,
        created_at: '2025-10-21T12:00:00Z',
      };

      const viewModel = mapOwnedValuationDtoToViewModel(dto);

      expect(viewModel.bricksetNumber).toBe('00123');
    });

    it('should format large brickset numbers', () => {
      const dto: OwnedValuationListItemDTO = {
        id: 1,
        brickset: {
          id: 10,
          number: 9999999,
        },
        value: 450,
        currency: 'PLN',
        likes_count: 5,
        created_at: '2025-10-21T12:00:00Z',
      };

      const viewModel = mapOwnedValuationDtoToViewModel(dto);

      expect(viewModel.bricksetNumber).toBe('9999999');
    });

    it('should format value as currency string', () => {
      const dto: OwnedValuationListItemDTO = {
        id: 1,
        brickset: {
          id: 10,
          number: 12345,
        },
        value: 450,
        currency: 'PLN',
        likes_count: 5,
        created_at: '2025-10-21T12:00:00Z',
      };

      const viewModel = mapOwnedValuationDtoToViewModel(dto);

      expect(viewModel.valueFormatted).toBe('450 PLN');
    });

    it('should format different value amounts', () => {
      const testValues = [1, 100, 999, 1000, 999999];

      testValues.forEach((value) => {
        const dto: OwnedValuationListItemDTO = {
          id: 1,
          brickset: {
            id: 10,
            number: 12345,
          },
          value,
          currency: 'PLN',
          likes_count: 5,
          created_at: '2025-10-21T12:00:00Z',
        };

        const viewModel = mapOwnedValuationDtoToViewModel(dto);

        expect(viewModel.valueFormatted).toBe(`${value} PLN`);
      });
    });

    it('should convert ISO timestamp to relative time', () => {
      const dto: OwnedValuationListItemDTO = {
        id: 1,
        brickset: {
          id: 10,
          number: 12345,
        },
        value: 450,
        currency: 'PLN',
        likes_count: 5,
        created_at: '2025-10-21T12:00:00Z',
      };

      const viewModel = mapOwnedValuationDtoToViewModel(dto);

      expect(viewModel.createdAtRelative).toBeTruthy();
      expect(typeof viewModel.createdAtRelative).toBe('string');
    });

    it('should preserve ISO timestamp in createdAt field', () => {
      const isoDate = '2025-10-21T12:00:00Z';
      const dto: OwnedValuationListItemDTO = {
        id: 1,
        brickset: {
          id: 10,
          number: 12345,
        },
        value: 450,
        currency: 'PLN',
        likes_count: 5,
        created_at: isoDate,
      };

      const viewModel = mapOwnedValuationDtoToViewModel(dto);

      expect(viewModel.createdAt).toBe(isoDate);
    });

    it('should handle zero likes', () => {
      const dto: OwnedValuationListItemDTO = {
        id: 1,
        brickset: {
          id: 10,
          number: 12345,
        },
        value: 450,
        currency: 'PLN',
        likes_count: 0,
        created_at: '2025-10-21T12:00:00Z',
      };

      const viewModel = mapOwnedValuationDtoToViewModel(dto);

      expect(viewModel.likesCount).toBe(0);
    });

    it('should handle high like counts', () => {
      const dto: OwnedValuationListItemDTO = {
        id: 1,
        brickset: {
          id: 10,
          number: 12345,
        },
        value: 450,
        currency: 'PLN',
        likes_count: 999999,
        created_at: '2025-10-21T12:00:00Z',
      };

      const viewModel = mapOwnedValuationDtoToViewModel(dto);

      expect(viewModel.likesCount).toBe(999999);
    });

    it('should map multiple valuations independently', () => {
      const dtos: OwnedValuationListItemDTO[] = [
        {
          id: 1,
          brickset: { id: 10, number: 12345 },
          value: 450,
          currency: 'PLN',
          likes_count: 5,
          created_at: '2025-10-21T12:00:00Z',
        },
        {
          id: 2,
          brickset: { id: 20, number: 67890 },
          value: 250,
          currency: 'PLN',
          likes_count: 3,
          created_at: '2025-10-20T12:00:00Z',
        },
      ];

      const viewModels = dtos.map(mapOwnedValuationDtoToViewModel);

      expect(viewModels).toHaveLength(2);
      expect(viewModels[0].bricksetId).toBe(10);
      expect(viewModels[1].bricksetId).toBe(20);
      expect(viewModels[0].valueFormatted).toBe('450 PLN');
      expect(viewModels[1].valueFormatted).toBe('250 PLN');
    });
  });
});
