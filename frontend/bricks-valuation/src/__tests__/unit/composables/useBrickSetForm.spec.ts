import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useBrickSetForm, ValidationError, DuplicateError } from '@/composables/useBrickSetForm';
import axiosInstance from '@/config/axios';

vi.mock('@/config/axios');
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string) => key,
  }),
}));

describe('useBrickSetForm Composable', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Initialization', () => {
    it('initializes with default form data', () => {
      const form = useBrickSetForm();

      expect(form.formData.number).toBe('');
      expect(form.formData.productionStatus).toBe('ACTIVE');
      expect(form.formData.completeness).toBe('COMPLETE');
      expect(form.formData.hasInstructions).toBe(false);
      expect(form.formData.hasBox).toBe(false);
      expect(form.formData.isFactorySealed).toBe(false);
      expect(form.formData.ownerInitialEstimate).toBe(null);
      expect(form.formData.isDirty).toBe(false);
    });

    it('initializes with empty field errors', () => {
      const form = useBrickSetForm();

      expect(Object.keys(form.fieldErrors).length).toBe(0);
    });

    it('initializes with isSubmitting as false', () => {
      const form = useBrickSetForm();

      expect(form.isSubmitting.value).toBe(false);
    });

    it('initializes with hasErrors as false', () => {
      const form = useBrickSetForm();

      expect(form.hasErrors.value).toBe(false);
    });
  });

  describe('Field Validation', () => {
    it('validates required number field', () => {
      const form = useBrickSetForm();
      form.formData.number = '';

      const isValid = form.validateField('number');

      expect(isValid).toBe(false);
      expect(form.fieldErrors.number).toBe('bricksets.create.errors.numberRequired');
    });

    it('validates number format', () => {
      const form = useBrickSetForm();
      form.formData.number = 'abc';

      const isValid = form.validateField('number');

      expect(isValid).toBe(false);
      expect(form.fieldErrors.number).toBe('bricksets.create.errors.numberFormat');
    });

    it('validates number range - too low', () => {
      const form = useBrickSetForm();
      // Negative numbers fail the regex pattern test (which expects digits only)
      // So this test actually validates the format error, not range error
      form.formData.number = '-1';

      const isValid = form.validateField('number');

      expect(isValid).toBe(false);
      // -1 fails regex pattern (/^\d+$/) so it's a format error
      expect(form.fieldErrors.number).toBe('bricksets.create.errors.numberFormat');
    });

    it('validates number range - too high', () => {
      const form = useBrickSetForm();
      form.formData.number = '99999999';

      const isValid = form.validateField('number');

      expect(isValid).toBe(false);
      expect(form.fieldErrors.number).toBe('bricksets.create.errors.numberRange');
    });

    it('accepts valid number', () => {
      const form = useBrickSetForm();
      form.formData.number = '10331';

      const isValid = form.validateField('number');

      expect(isValid).toBe(true);
      expect(form.fieldErrors.number).toBeUndefined();
    });

    it('validates production status', () => {
      const form = useBrickSetForm();
      form.formData.productionStatus = '' as unknown as typeof form.formData.productionStatus;

      const isValid = form.validateField('productionStatus');

      expect(isValid).toBe(false);
      expect(form.fieldErrors.productionStatus).toBe(
        'bricksets.create.errors.productionStatusRequired'
      );
    });

    it('validates completeness', () => {
      const form = useBrickSetForm();
      form.formData.completeness = '' as unknown as typeof form.formData.completeness;

      const isValid = form.validateField('completeness');

      expect(isValid).toBe(false);
      expect(form.fieldErrors.completeness).toBe('bricksets.create.errors.completenessRequired');
    });

    it('validates optional estimate format', () => {
      const form = useBrickSetForm();
      form.formData.ownerInitialEstimate = 'abc';

      const isValid = form.validateField('ownerInitialEstimate');

      expect(isValid).toBe(false);
      expect(form.fieldErrors.ownerInitialEstimate).toBe('bricksets.create.errors.estimateFormat');
    });

    it('validates optional estimate range', () => {
      const form = useBrickSetForm();
      form.formData.ownerInitialEstimate = '9999999';

      const isValid = form.validateField('ownerInitialEstimate');

      expect(isValid).toBe(false);
      expect(form.fieldErrors.ownerInitialEstimate).toBe('bricksets.create.errors.estimateRange');
    });

    it('accepts empty estimate (optional field)', () => {
      const form = useBrickSetForm();
      form.formData.ownerInitialEstimate = null;

      const isValid = form.validateField('ownerInitialEstimate');

      expect(isValid).toBe(true);
      expect(form.fieldErrors.ownerInitialEstimate).toBeUndefined();
    });

    it('accepts valid estimate', () => {
      const form = useBrickSetForm();
      form.formData.ownerInitialEstimate = '500';

      const isValid = form.validateField('ownerInitialEstimate');

      expect(isValid).toBe(true);
      expect(form.fieldErrors.ownerInitialEstimate).toBeUndefined();
    });

    it('boolean fields are always valid', () => {
      const form = useBrickSetForm();

      expect(form.validateField('hasInstructions')).toBe(true);
      expect(form.validateField('hasBox')).toBe(true);
      expect(form.validateField('isFactorySealed')).toBe(true);
    });
  });

  describe('Form Validation', () => {
    it('validates entire form and returns false if fields are invalid', () => {
      const form = useBrickSetForm();
      form.formData.number = '';

      const isValid = form.validateForm();

      expect(isValid).toBe(false);
      expect(form.fieldErrors.number).toBeDefined();
    });

    it('validates entire form and returns true if all fields are valid', () => {
      const form = useBrickSetForm();
      form.formData.number = '10331';
      form.formData.productionStatus = 'ACTIVE';
      form.formData.completeness = 'COMPLETE';

      const isValid = form.validateForm();

      expect(isValid).toBe(true);
      expect(Object.keys(form.fieldErrors).length).toBe(0);
    });
  });

  describe('setFieldValue', () => {
    it('sets field value and marks form as dirty', () => {
      const form = useBrickSetForm();

      form.setFieldValue('number', '10331');

      expect(form.formData.number).toBe('10331');
      expect(form.formData.isDirty).toBe(true);
    });

    it('clears field error when value changes', () => {
      const form = useBrickSetForm();
      form.fieldErrors.number = 'Error';

      form.setFieldValue('number', '10331');

      expect(form.fieldErrors.number).toBeUndefined();
    });
  });

  describe('resetForm', () => {
    it('resets form to initial state', () => {
      const form = useBrickSetForm();
      form.formData.number = '10331';
      form.formData.hasInstructions = true;
      form.formData.isDirty = true;
      form.fieldErrors.number = 'Error';

      form.resetForm();

      expect(form.formData.number).toBe('');
      expect(form.formData.hasInstructions).toBe(false);
      expect(form.formData.isDirty).toBe(false);
      expect(Object.keys(form.fieldErrors).length).toBe(0);
    });
  });

  describe('submitForm', () => {
    it('submits form with valid data', async () => {
      const mockResponse = {
        data: {
          id: 1,
          number: 10331,
          production_status: 'ACTIVE',
          completeness: 'COMPLETE',
          has_instructions: false,
          has_box: false,
          is_factory_sealed: false,
          owner_initial_estimate: null,
          owner_id: 1,
          valuations_count: 0,
          total_likes: 0,
          top_valuation: null,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        },
      };

      vi.mocked(axiosInstance.post).mockResolvedValueOnce(mockResponse);

      const form = useBrickSetForm();
      form.formData.number = '10331';
      form.formData.productionStatus = 'ACTIVE';
      form.formData.completeness = 'COMPLETE';

      const result = await form.submitForm();

      expect(result).toEqual(mockResponse.data);
      expect(axiosInstance.post).toHaveBeenCalledWith(
        '/v1/bricksets',
        {
          number: 10331,
          production_status: 'ACTIVE',
          completeness: 'COMPLETE',
          has_instructions: false,
          has_box: false,
          is_factory_sealed: false,
          owner_initial_estimate: null,
        },
        { withCredentials: true }
      );
    });

    it('throws error if form validation fails', async () => {
      const form = useBrickSetForm();
      form.formData.number = '';

      await expect(form.submitForm()).rejects.toThrow('Form validation failed');
    });

    it('handles 400 validation error from API', async () => {
      const mockError = {
        response: {
          status: 400,
          data: {
            errors: {
              number: ['Number is required'],
            },
          },
        },
      };

      vi.mocked(axiosInstance.post).mockRejectedValueOnce(mockError);

      const form = useBrickSetForm();
      form.formData.number = '10331';
      form.formData.productionStatus = 'ACTIVE';
      form.formData.completeness = 'COMPLETE';

      await expect(form.submitForm()).rejects.toThrow(ValidationError);
      expect(form.fieldErrors.number).toBe('Number is required');
    });

    it('handles 409 duplicate error from API', async () => {
      const mockError = {
        response: {
          status: 409,
          data: {
            detail: 'Duplicate set',
            constraint: 'brickset_global_identity',
          },
        },
      };

      vi.mocked(axiosInstance.post).mockRejectedValueOnce(mockError);

      const form = useBrickSetForm();
      form.formData.number = '10331';
      form.formData.productionStatus = 'ACTIVE';
      form.formData.completeness = 'COMPLETE';

      await expect(form.submitForm()).rejects.toThrow(DuplicateError);
    });

    it('handles 401 unauthorized error', async () => {
      const mockError = {
        response: {
          status: 401,
        },
      };

      vi.mocked(axiosInstance.post).mockRejectedValueOnce(mockError);

      const form = useBrickSetForm();
      form.formData.number = '10331';
      form.formData.productionStatus = 'ACTIVE';
      form.formData.completeness = 'COMPLETE';

      await expect(form.submitForm()).rejects.toThrow('errors.unauthorized');
    });

    it('handles 500 server error', async () => {
      const mockError = {
        response: {
          status: 500,
        },
      };

      vi.mocked(axiosInstance.post).mockRejectedValueOnce(mockError);

      const form = useBrickSetForm();
      form.formData.number = '10331';
      form.formData.productionStatus = 'ACTIVE';
      form.formData.completeness = 'COMPLETE';

      await expect(form.submitForm()).rejects.toThrow('errors.serverError');
    });

    it('sets isSubmitting to true during submission', async () => {
      const mockResponse = { data: { id: 1 } };
      vi.mocked(axiosInstance.post).mockResolvedValueOnce(mockResponse);

      const form = useBrickSetForm();
      form.formData.number = '10331';
      form.formData.productionStatus = 'ACTIVE';
      form.formData.completeness = 'COMPLETE';

      const promise = form.submitForm();
      expect(form.isSubmitting.value).toBe(true);

      await promise;
      expect(form.isSubmitting.value).toBe(false);
    });
  });

  describe('Computed Properties', () => {
    it('hasErrors returns true when there are field errors', () => {
      const form = useBrickSetForm();
      form.fieldErrors.number = 'Error';

      expect(form.hasErrors.value).toBe(true);
    });

    it('hasErrors returns false when there are no field errors', () => {
      const form = useBrickSetForm();

      expect(form.hasErrors.value).toBe(false);
    });

    it('isDirty returns true when form is modified', () => {
      const form = useBrickSetForm();
      form.formData.isDirty = true;

      expect(form.isDirty.value).toBe(true);
    });

    it('isDirty returns false when form is not modified', () => {
      const form = useBrickSetForm();

      expect(form.isDirty.value).toBe(false);
    });
  });
});
