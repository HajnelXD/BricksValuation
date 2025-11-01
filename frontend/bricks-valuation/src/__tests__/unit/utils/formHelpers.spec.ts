import { describe, it, expect } from 'vitest';
import {
  brickSetToFormData,
  generateUpdateDTO,
  validateSetNumber,
  validateEstimate,
  cloneFormData,
  isFormDataEqual,
} from '@/utils/formHelpers';
import type { BrickSetEditDetailDTO, BrickSetFormData } from '@/types/bricksets';

describe('formHelpers', () => {
  describe('brickSetToFormData', () => {
    it('converts BrickSetEditDetailDTO to BrickSetFormData correctly', () => {
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

      const result = brickSetToFormData(mockBrickSet);

      expect(result.number).toBe('10331');
      expect(result.productionStatus).toBe('ACTIVE');
      expect(result.completeness).toBe('COMPLETE');
      expect(result.hasInstructions).toBe(true);
      expect(result.hasBox).toBe(true);
      expect(result.isFactorySealed).toBe(false);
      expect(result.ownerInitialEstimate).toBe('500');
      expect(result.isDirty).toBe(false);
    });

    it('handles null owner_initial_estimate', () => {
      const mockBrickSet: BrickSetEditDetailDTO = {
        id: 1,
        number: 10331,
        production_status: 'RETIRED',
        completeness: 'INCOMPLETE',
        has_instructions: false,
        has_box: false,
        is_factory_sealed: false,
        owner_initial_estimate: null,
        owner_id: 1,
        valuations: [],
        valuations_count: 0,
        total_likes: 0,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        editable: false,
        deletable: false,
        owner: {
          id: 1,
          username: 'testuser',
        },
      };

      const result = brickSetToFormData(mockBrickSet);

      expect(result.ownerInitialEstimate).toBe(null);
    });
  });

  describe('generateUpdateDTO', () => {
    it('generates DTO with only changed fields', () => {
      const formData: BrickSetFormData = {
        number: '10332',
        productionStatus: 'RETIRED',
        completeness: 'COMPLETE',
        hasInstructions: true,
        hasBox: false,
        isFactorySealed: false,
        ownerInitialEstimate: '600',
        isDirty: true,
      };

      const originalData: BrickSetFormData = {
        number: '10331',
        productionStatus: 'ACTIVE',
        completeness: 'COMPLETE',
        hasInstructions: true,
        hasBox: true,
        isFactorySealed: false,
        ownerInitialEstimate: '500',
        isDirty: false,
      };

      const result = generateUpdateDTO(formData, originalData);

      expect(result.number).toBe(10332);
      expect(result.production_status).toBe('RETIRED');
      expect(result.has_box).toBe(false);
      expect(result.owner_initial_estimate).toBe(600);
      expect(result.completeness).toBeUndefined();
      expect(result.has_instructions).toBeUndefined();
    });

    it('returns empty object when no changes', () => {
      const formData: BrickSetFormData = {
        number: '10331',
        productionStatus: 'ACTIVE',
        completeness: 'COMPLETE',
        hasInstructions: true,
        hasBox: true,
        isFactorySealed: false,
        ownerInitialEstimate: '500',
        isDirty: false,
      };

      const result = generateUpdateDTO(formData, formData);

      expect(Object.keys(result).length).toBe(0);
    });

    it('handles null to value change for owner_initial_estimate', () => {
      const formData: BrickSetFormData = {
        number: '10331',
        productionStatus: 'ACTIVE',
        completeness: 'COMPLETE',
        hasInstructions: true,
        hasBox: true,
        isFactorySealed: false,
        ownerInitialEstimate: '500',
        isDirty: true,
      };

      const originalData: BrickSetFormData = {
        ...formData,
        ownerInitialEstimate: null,
      };

      const result = generateUpdateDTO(formData, originalData);

      expect(result.owner_initial_estimate).toBe(500);
    });

    it('handles value to null change for owner_initial_estimate', () => {
      const formData: BrickSetFormData = {
        number: '10331',
        productionStatus: 'ACTIVE',
        completeness: 'COMPLETE',
        hasInstructions: true,
        hasBox: true,
        isFactorySealed: false,
        ownerInitialEstimate: null,
        isDirty: true,
      };

      const originalData: BrickSetFormData = {
        ...formData,
        ownerInitialEstimate: '500',
      };

      const result = generateUpdateDTO(formData, originalData);

      expect(result.owner_initial_estimate).toBe(null);
    });
  });

  describe('validateSetNumber', () => {
    it('returns null for valid number', () => {
      expect(validateSetNumber('10331')).toBe(null);
      expect(validateSetNumber('1')).toBe(null);
      expect(validateSetNumber('9999999')).toBe(null);
    });

    it('returns error for empty string', () => {
      expect(validateSetNumber('')).toBe('To pole jest wymagane');
      expect(validateSetNumber('   ')).toBe('To pole jest wymagane');
    });

    it('returns error for non-numeric characters', () => {
      const error = 'Numer zestawu może zawierać tylko cyfry (1-7 znaków)';
      expect(validateSetNumber('abc')).toBe(error);
      expect(validateSetNumber('123abc')).toBe(error);
      expect(validateSetNumber('12.34')).toBe(error);
    });

    it('returns error for number too long', () => {
      const error = 'Numer zestawu może zawierać tylko cyfry (1-7 znaków)';
      expect(validateSetNumber('12345678')).toBe(error);
    });
  });

  describe('validateEstimate', () => {
    it('returns null for valid estimate', () => {
      expect(validateEstimate('100')).toBe(null);
      expect(validateEstimate('999999')).toBe(null);
      expect(validateEstimate('1')).toBe(null);
    });

    it('returns null for null or empty string (optional field)', () => {
      expect(validateEstimate(null)).toBe(null);
      expect(validateEstimate('')).toBe(null);
    });

    it('returns error for non-numeric value', () => {
      expect(validateEstimate('abc')).toBe('Wartość musi być liczbą');
      expect(validateEstimate('12.34abc')).toBe('Wartość musi być liczbą');
    });

    it('returns error for zero or negative value', () => {
      expect(validateEstimate('0')).toBe('Wartość musi być większa od 0');
      expect(validateEstimate('-100')).toBe('Wartość musi być większa od 0');
    });

    it('returns error for value >= 1000000', () => {
      expect(validateEstimate('1000000')).toBe('Wartość nie może przekraczać 999999');
      expect(validateEstimate('9999999')).toBe('Wartość nie może przekraczać 999999');
    });
  });

  describe('cloneFormData', () => {
    it('creates a deep copy of form data', () => {
      const original: BrickSetFormData = {
        number: '10331',
        productionStatus: 'ACTIVE',
        completeness: 'COMPLETE',
        hasInstructions: true,
        hasBox: true,
        isFactorySealed: false,
        ownerInitialEstimate: '500',
        isDirty: false,
      };

      const cloned = cloneFormData(original);

      expect(cloned).toEqual(original);
      expect(cloned).not.toBe(original);

      // Modify clone and check original is unchanged
      cloned.number = '99999';
      expect(original.number).toBe('10331');
    });
  });

  describe('isFormDataEqual', () => {
    it('returns true for equal form data', () => {
      const formData1: BrickSetFormData = {
        number: '10331',
        productionStatus: 'ACTIVE',
        completeness: 'COMPLETE',
        hasInstructions: true,
        hasBox: true,
        isFactorySealed: false,
        ownerInitialEstimate: '500',
        isDirty: false,
      };

      const formData2: BrickSetFormData = {
        number: '10331',
        productionStatus: 'ACTIVE',
        completeness: 'COMPLETE',
        hasInstructions: true,
        hasBox: true,
        isFactorySealed: false,
        ownerInitialEstimate: '500',
        isDirty: false,
      };

      expect(isFormDataEqual(formData1, formData2)).toBe(true);
    });

    it('returns false for different form data', () => {
      const formData1: BrickSetFormData = {
        number: '10331',
        productionStatus: 'ACTIVE',
        completeness: 'COMPLETE',
        hasInstructions: true,
        hasBox: true,
        isFactorySealed: false,
        ownerInitialEstimate: '500',
        isDirty: false,
      };

      const formData2: BrickSetFormData = {
        ...formData1,
        number: '10332',
      };

      expect(isFormDataEqual(formData1, formData2)).toBe(false);
    });
  });
});
