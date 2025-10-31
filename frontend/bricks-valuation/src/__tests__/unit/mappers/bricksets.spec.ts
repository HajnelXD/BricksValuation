import { describe, it, expect } from 'vitest';
import {
  formatCurrency,
  formatProductionStatusLabel,
  formatCompletenessLabel,
  formatRelativeTime,
  validateOrderingOption,
  parseBooleanQueryParam,
  mapBrickSetDtoToListItemViewModel,
  mapBrickSetDtoToViewModel,
  mapTopValuationToViewModel,
  serializeBooleanQueryParam,
  mapValuationDtoToViewModel,
  mapValuationDtoToTopViewModel,
  mapBrickSetDetailDtoToViewModel,
} from '@/mappers/bricksets';
import type { BrickSetListItemDTO, ValuationDTO, BrickSetDetailDTO } from '@/types/bricksets';

describe('Bricksets Mappers - Fixed', () => {
  describe('formatCurrency', () => {
    it('formats number to PLN currency', () => {
      expect(formatCurrency(100)).toBe('100 PLN');
    });

    it('handles zero value', () => {
      expect(formatCurrency(0)).toBe('0 PLN');
    });

    it('handles large numbers', () => {
      expect(formatCurrency(10000)).toBe('10000 PLN');
    });

    it('handles decimal values', () => {
      expect(formatCurrency(123.45)).toBe('123.45 PLN');
    });

    it('handles negative values', () => {
      expect(formatCurrency(-50)).toBe('-50 PLN');
    });
  });

  describe('formatProductionStatusLabel', () => {
    it('returns Polish label for ACTIVE', () => {
      expect(formatProductionStatusLabel('ACTIVE')).toBe('Aktywny');
    });

    it('returns Polish label for RETIRED', () => {
      expect(formatProductionStatusLabel('RETIRED')).toBe('Wycofany');
    });
  });

  describe('formatCompletenessLabel', () => {
    it('returns Polish label for COMPLETE', () => {
      expect(formatCompletenessLabel('COMPLETE')).toBe('Kompletny');
    });

    it('returns Polish label for INCOMPLETE', () => {
      expect(formatCompletenessLabel('INCOMPLETE')).toBe('Niekompletny');
    });
  });

  describe('formatRelativeTime', () => {
    it('formats current time as just now', () => {
      const now = new Date().toISOString();
      const result = formatRelativeTime(now);
      expect(result).toBe('przed chwilą');
    });

    it('formats time from 1 minute ago', () => {
      const oneMinuteAgo = new Date();
      oneMinuteAgo.setMinutes(oneMinuteAgo.getMinutes() - 1);
      const result = formatRelativeTime(oneMinuteAgo.toISOString());
      expect(result).toContain('minutę temu');
    });

    it('formats time from yesterday', () => {
      const yesterday = new Date();
      yesterday.setDate(yesterday.getDate() - 1);
      const result = formatRelativeTime(yesterday.toISOString());
      expect(result).toContain('dzień temu');
    });

    it('formats time from multiple days ago', () => {
      const threeDaysAgo = new Date();
      threeDaysAgo.setDate(threeDaysAgo.getDate() - 3);
      const result = formatRelativeTime(threeDaysAgo.toISOString());
      expect(result).toContain('dni temu');
    });

    it('handles hours ago correctly', () => {
      const twoHoursAgo = new Date();
      twoHoursAgo.setHours(twoHoursAgo.getHours() - 2);
      const result = formatRelativeTime(twoHoursAgo.toISOString());
      expect(result).toContain('godzin temu');
    });
  });

  describe('validateOrderingOption', () => {
    it('accepts valid ordering option -created_at', () => {
      expect(validateOrderingOption('-created_at')).toBe('-created_at');
    });

    it('returns default for invalid ordering option', () => {
      expect(validateOrderingOption('invalid_option')).toBe('-created_at');
    });

    it('returns default for null', () => {
      expect(validateOrderingOption(null)).toBe('-created_at');
    });
  });

  describe('parseBooleanQueryParam', () => {
    it('parses "true" string to boolean true', () => {
      expect(parseBooleanQueryParam('true')).toBe(true);
    });

    it('parses "false" string to boolean false', () => {
      expect(parseBooleanQueryParam('false')).toBe(false);
    });

    it('returns null for empty string', () => {
      expect(parseBooleanQueryParam('')).toBe(null);
    });

    it('returns null for undefined', () => {
      expect(parseBooleanQueryParam(undefined)).toBe(null);
    });

    it('returns null for invalid value', () => {
      expect(parseBooleanQueryParam('maybe')).toBe(null);
    });
  });

  describe('serializeBooleanQueryParam', () => {
    it('serializes true to "true"', () => {
      expect(serializeBooleanQueryParam(true)).toBe('true');
    });

    it('serializes false to null', () => {
      expect(serializeBooleanQueryParam(false)).toBe(null);
    });

    it('serializes null to null', () => {
      expect(serializeBooleanQueryParam(null)).toBe(null);
    });
  });

  describe('mapTopValuationToViewModel', () => {
    it('maps top valuation DTO to ViewModel correctly', () => {
      const topValuationDto = {
        id: 1,
        value: 200,
        currency: 'PLN',
        likes_count: 10,
        user_id: 2,
      };

      const viewModel = mapTopValuationToViewModel(topValuationDto);

      expect(viewModel).toBeDefined();
      expect(viewModel?.id).toBe(1);
      expect(viewModel?.valueFormatted).toContain('PLN');
      expect(viewModel?.likesCount).toBe(10);
    });

    it('returns undefined when top valuation is null', () => {
      const viewModel = mapTopValuationToViewModel(null);
      expect(viewModel).toBeUndefined();
    });

    it('returns undefined when top valuation is undefined', () => {
      const viewModel = mapTopValuationToViewModel(undefined);
      expect(viewModel).toBeUndefined();
    });
  });

  describe('mapBrickSetDtoToViewModel', () => {
    const createMockDto = (overrides: Partial<BrickSetListItemDTO> = {}): BrickSetListItemDTO => ({
      id: 1,
      number: 10001,
      production_status: 'ACTIVE',
      completeness: 'COMPLETE',
      has_instructions: true,
      has_box: true,
      is_factory_sealed: false,
      owner_id: 1,
      owner_initial_estimate: 150,
      valuations_count: 5,
      total_likes: 23,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      top_valuation: undefined,
      ...overrides,
    });

    it('maps complete DTO to ViewModel correctly', () => {
      const dto = createMockDto({
        top_valuation: {
          id: 1,
          value: 200,
          currency: 'PLN',
          likes_count: 10,
          user_id: 2,
        },
      });

      const viewModel = mapBrickSetDtoToViewModel(dto);

      expect(viewModel.id).toBe(1);
      expect(viewModel.number).toBe('10001');
      expect(viewModel.productionStatusLabel).toBe('Aktywny');
      expect(viewModel.completenessLabel).toBe('Kompletny');
      expect(viewModel.hasInstructions).toBe(true);
      expect(viewModel.hasBox).toBe(true);
      expect(viewModel.isFactorySealed).toBe(false);
      expect(viewModel.valuationsCount).toBe(5);
      expect(viewModel.totalLikes).toBe(23);
      expect(viewModel.topValuation).toBeDefined();
      expect(viewModel.topValuation?.valueFormatted).toContain('PLN');
    });

    it('handles minimal DTO with required fields only', () => {
      const dto = createMockDto({
        owner_initial_estimate: null,
        top_valuation: undefined,
      });

      const viewModel = mapBrickSetDtoToViewModel(dto);

      expect(viewModel.id).toBe(1);
      expect(viewModel.number).toBe('10001');
      expect(viewModel.topValuation).toBeUndefined();
    });

    it('correctly formats created_at as relative time', () => {
      const dto = createMockDto();
      const viewModel = mapBrickSetDtoToViewModel(dto);

      expect(viewModel.createdAtRelative).toBeTruthy();
      expect(typeof viewModel.createdAtRelative).toBe('string');
    });
  });

  describe('mapBrickSetDtoToListItemViewModel', () => {
    const createMockDto = (overrides: Partial<BrickSetListItemDTO> = {}): BrickSetListItemDTO => ({
      id: 1,
      number: 10001,
      production_status: 'ACTIVE',
      completeness: 'COMPLETE',
      has_instructions: true,
      has_box: true,
      is_factory_sealed: false,
      owner_id: 1,
      owner_initial_estimate: 150,
      valuations_count: 5,
      total_likes: 23,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      top_valuation: undefined,
      ...overrides,
    });

    it('maps DTO to ListItemViewModel with createdAt field', () => {
      const now = new Date().toISOString();
      const dto = createMockDto({ created_at: now });

      const viewModel = mapBrickSetDtoToListItemViewModel(dto);

      expect(viewModel.id).toBe(1);
      expect(viewModel.createdAt).toBe(now);
    });

    it('includes all fields from CardViewModel', () => {
      const dto = createMockDto();
      const viewModel = mapBrickSetDtoToListItemViewModel(dto);

      expect(viewModel.number).toBe('10001');
      expect(viewModel.productionStatusLabel).toBe('Aktywny');
      expect(viewModel.completenessLabel).toBe('Kompletny');
    });
  });

  describe('Number padding', () => {
    it('pads number with leading zeros to 5 digits', () => {
      const dto: BrickSetListItemDTO = {
        id: 1,
        number: 1,
        production_status: 'ACTIVE',
        completeness: 'COMPLETE',
        has_instructions: false,
        has_box: false,
        is_factory_sealed: false,
        owner_id: 1,
        owner_initial_estimate: 0,
        valuations_count: 0,
        total_likes: 0,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        top_valuation: undefined,
      };

      const viewModel = mapBrickSetDtoToViewModel(dto);
      expect(viewModel.number).toBe('00001');
    });

    it('does not pad numbers already 5+ digits', () => {
      const dto: BrickSetListItemDTO = {
        id: 1,
        number: 123456,
        production_status: 'ACTIVE',
        completeness: 'COMPLETE',
        has_instructions: false,
        has_box: false,
        is_factory_sealed: false,
        owner_id: 1,
        owner_initial_estimate: 0,
        valuations_count: 0,
        total_likes: 0,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        top_valuation: undefined,
      };

      const viewModel = mapBrickSetDtoToViewModel(dto);
      expect(viewModel.number).toBe('123456');
    });
  });

  describe('mapValuationDtoToViewModel', () => {
    it('maps valuation DTO to ViewModel correctly', () => {
      const now = new Date().toISOString();
      const dto: ValuationDTO = {
        id: 1,
        user_id: 42,
        value: 350,
        currency: 'PLN',
        comment: 'Great set!',
        likes_count: 15,
        created_at: now,
      };

      const viewModel = mapValuationDtoToViewModel(dto);

      expect(viewModel.id).toBe(1);
      expect(viewModel.userId).toBe(42);
      expect(viewModel.valueFormatted).toBe('350 PLN');
      expect(viewModel.comment).toBe('Great set!');
      expect(viewModel.likesCount).toBe(15);
      expect(viewModel.createdAt).toBe(now);
      expect(viewModel.createdAtRelative).toBeTruthy();
      expect(typeof viewModel.createdAtRelative).toBe('string');
    });

    it('handles empty comment', () => {
      const dto: ValuationDTO = {
        id: 2,
        user_id: 10,
        value: 100,
        currency: 'PLN',
        comment: '',
        likes_count: 0,
        created_at: new Date().toISOString(),
      };

      const viewModel = mapValuationDtoToViewModel(dto);

      expect(viewModel.comment).toBe('');
      expect(viewModel.likesCount).toBe(0);
    });
  });

  describe('mapValuationDtoToTopViewModel', () => {
    it('maps valuation DTO to TopViewModel correctly', () => {
      const now = new Date().toISOString();
      const dto: ValuationDTO = {
        id: 5,
        user_id: 99,
        value: 500,
        currency: 'PLN',
        comment: 'Excellent condition',
        likes_count: 25,
        created_at: now,
      };

      const viewModel = mapValuationDtoToTopViewModel(dto);

      expect(viewModel.id).toBe(5);
      expect(viewModel.userId).toBe(99);
      expect(viewModel.valueFormatted).toBe('500 PLN');
      expect(viewModel.comment).toBe('Excellent condition');
      expect(viewModel.likesCount).toBe(25);
      expect(viewModel.createdAtRelative).toBeTruthy();
      expect(typeof viewModel.createdAtRelative).toBe('string');
    });
  });

  describe('mapBrickSetDetailDtoToViewModel', () => {
    const createMockDetailDto = (
      overrides: Partial<BrickSetDetailDTO> = {}
    ): BrickSetDetailDTO => ({
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
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      ...overrides,
    });

    it('maps BrickSetDetailDTO to ViewModel correctly', () => {
      const dto = createMockDetailDto({
        valuations: [
          {
            id: 1,
            user_id: 10,
            value: 450,
            currency: 'PLN',
            comment: 'Good price',
            likes_count: 10,
            created_at: new Date().toISOString(),
          },
        ],
        valuations_count: 1,
        total_likes: 10,
      });

      const viewModel = mapBrickSetDetailDtoToViewModel(dto);

      expect(viewModel.id).toBe(1);
      expect(viewModel.number).toBe('10331');
      expect(viewModel.productionStatusLabel).toBe('Aktywny');
      expect(viewModel.completenessLabel).toBe('Kompletny');
      expect(viewModel.hasInstructions).toBe(true);
      expect(viewModel.hasBox).toBe(true);
      expect(viewModel.isFactorySealed).toBe(false);
      expect(viewModel.ownerInitialEstimate).toBe(500);
      expect(viewModel.ownerId).toBe(1);
      expect(viewModel.valuationsCount).toBe(1);
      expect(viewModel.totalLikes).toBe(10);
      expect(viewModel.valuations).toHaveLength(1);
      expect(viewModel.topValuation).toBeDefined();
      expect(viewModel.topValuation?.valueFormatted).toBe('450 PLN');
    });

    it('handles empty valuations array', () => {
      const dto = createMockDetailDto({ valuations: [] });

      const viewModel = mapBrickSetDetailDtoToViewModel(dto);

      expect(viewModel.valuations).toHaveLength(0);
      expect(viewModel.topValuation).toBeNull();
    });

    it('sorts valuations by likes_count descending', () => {
      const dto = createMockDetailDto({
        valuations: [
          {
            id: 1,
            user_id: 10,
            value: 400,
            currency: 'PLN',
            comment: 'First',
            likes_count: 5,
            created_at: '2024-01-01T10:00:00Z',
          },
          {
            id: 2,
            user_id: 11,
            value: 450,
            currency: 'PLN',
            comment: 'Second',
            likes_count: 15,
            created_at: '2024-01-02T10:00:00Z',
          },
          {
            id: 3,
            user_id: 12,
            value: 500,
            currency: 'PLN',
            comment: 'Third',
            likes_count: 10,
            created_at: '2024-01-03T10:00:00Z',
          },
        ],
      });

      const viewModel = mapBrickSetDetailDtoToViewModel(dto);

      expect(viewModel.valuations).toHaveLength(3);
      expect(viewModel.valuations[0].likesCount).toBe(15);
      expect(viewModel.valuations[1].likesCount).toBe(10);
      expect(viewModel.valuations[2].likesCount).toBe(5);
      expect(viewModel.topValuation?.id).toBe(2);
    });

    it('sorts valuations with same likes by created_at ascending', () => {
      const dto = createMockDetailDto({
        valuations: [
          {
            id: 1,
            user_id: 10,
            value: 400,
            currency: 'PLN',
            comment: 'First',
            likes_count: 10,
            created_at: '2024-01-03T10:00:00Z',
          },
          {
            id: 2,
            user_id: 11,
            value: 450,
            currency: 'PLN',
            comment: 'Second',
            likes_count: 10,
            created_at: '2024-01-01T10:00:00Z',
          },
          {
            id: 3,
            user_id: 12,
            value: 500,
            currency: 'PLN',
            comment: 'Third',
            likes_count: 10,
            created_at: '2024-01-02T10:00:00Z',
          },
        ],
      });

      const viewModel = mapBrickSetDetailDtoToViewModel(dto);

      expect(viewModel.valuations).toHaveLength(3);
      expect(viewModel.valuations[0].id).toBe(2); // earliest date
      expect(viewModel.valuations[1].id).toBe(3); // middle date
      expect(viewModel.valuations[2].id).toBe(1); // latest date
      expect(viewModel.topValuation?.id).toBe(2);
    });

    it('handles null owner_initial_estimate', () => {
      const dto = createMockDetailDto({ owner_initial_estimate: null });

      const viewModel = mapBrickSetDetailDtoToViewModel(dto);

      expect(viewModel.ownerInitialEstimate).toBeNull();
    });

    it('formats number with leading zeros', () => {
      const dto = createMockDetailDto({ number: 123 });

      const viewModel = mapBrickSetDetailDtoToViewModel(dto);

      expect(viewModel.number).toBe('00123');
    });
  });
});
