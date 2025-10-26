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
} from '@/mappers/bricksets';
import type { BrickSetListItemDTO } from '@/types/bricksets';

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
});
