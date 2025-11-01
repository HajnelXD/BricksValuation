import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  useValuationForm,
  ValuationValidationError,
  ValuationDuplicateError,
} from '@/composables/useValuationForm';
import apiClient from '@/config/axios';

vi.mock('@/config/axios');
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key: string) => key,
  }),
}));

describe('useValuationForm Composable', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Initialization', () => {
    it('initializes with default form data', () => {
      const form = useValuationForm(123);

      expect(form.formData.value.value).toBe(null);
      expect(form.formData.value.comment).toBe('');
    });

    it('initializes with empty errors', () => {
      const form = useValuationForm(123);

      expect(Object.keys(form.errors.value).length).toBe(0);
    });

    it('initializes with isSubmitting as false', () => {
      const form = useValuationForm(123);

      expect(form.isSubmitting.value).toBe(false);
    });

    it('initializes with empty touched fields', () => {
      const form = useValuationForm(123);

      expect(form.touchedFields.value.size).toBe(0);
    });

    it('initializes form as invalid', () => {
      const form = useValuationForm(123);

      expect(form.isFormValid.value).toBe(false);
    });

    it('disables submit button when form is invalid', () => {
      const form = useValuationForm(123);

      expect(form.canSubmit.value).toBe(false);
    });
  });

  describe('Field Validation - Value Field', () => {
    it('validates required value field', () => {
      const form = useValuationForm(123);

      const error = form.validateValueField(null);

      expect(error).toBe('valuation.errors.required');
    });

    it('validates undefined value field', () => {
      const form = useValuationForm(123);

      const error = form.validateValueField(undefined);

      expect(error).toBe('valuation.errors.required');
    });

    it('validates non-numeric value', () => {
      const form = useValuationForm(123);

      const error = form.validateValueField(NaN);

      expect(error).toBe('valuation.errors.notNumber');
    });

    it('validates minimum value (must be >= 1)', () => {
      const form = useValuationForm(123);

      const error = form.validateValueField(0);

      expect(error).toBe('valuation.errors.min');
    });

    it('validates maximum value (must be <= 999999)', () => {
      const form = useValuationForm(123);

      const error = form.validateValueField(1000000);

      expect(error).toBe('valuation.errors.max');
    });

    it('accepts valid value at minimum boundary', () => {
      const form = useValuationForm(123);

      const error = form.validateValueField(1);

      expect(error).toBeUndefined();
    });

    it('accepts valid value at maximum boundary', () => {
      const form = useValuationForm(123);

      const error = form.validateValueField(999999);

      expect(error).toBeUndefined();
    });

    it('accepts valid value in middle range', () => {
      const form = useValuationForm(123);

      const error = form.validateValueField(5000);

      expect(error).toBeUndefined();
    });

    it('accepts decimal values', () => {
      const form = useValuationForm(123);

      const error = form.validateValueField(1500.5);

      expect(error).toBeUndefined();
    });
  });

  describe('Field Validation - Comment Field', () => {
    it('accepts empty comment', () => {
      const form = useValuationForm(123);

      const error = form.validateCommentField('');

      expect(error).toBeUndefined();
    });

    it('validates comment max length (2000 chars)', () => {
      const form = useValuationForm(123);
      const longComment = 'a'.repeat(2001);

      const error = form.validateCommentField(longComment);

      expect(error).toBe('valuation.errors.commentTooLong');
    });

    it('accepts comment at max length boundary', () => {
      const form = useValuationForm(123);
      const maxComment = 'a'.repeat(2000);

      const error = form.validateCommentField(maxComment);

      expect(error).toBeUndefined();
    });

    it('accepts comment below max length', () => {
      const form = useValuationForm(123);

      const error = form.validateCommentField('This is a valid comment');

      expect(error).toBeUndefined();
    });
  });

  describe('Field State Management', () => {
    it('marks field as touched', () => {
      const form = useValuationForm(123);

      form.markFieldTouched('value');

      expect(form.touchedFields.value.has('value')).toBe(true);
    });

    it('validates single field and sets error', () => {
      const form = useValuationForm(123);
      form.formData.value.value = 0; // Invalid: below minimum

      form.validateField('value');

      expect(form.errors.value.value).toBe('valuation.errors.min');
    });

    it('clears previous error when validating field', () => {
      const form = useValuationForm(123);
      form.errors.value.value = 'old error';
      form.formData.value.value = 5000; // Valid value

      form.validateField('value');

      expect(form.errors.value.value).toBeUndefined();
    });

    it('validates comment field and sets error', () => {
      const form = useValuationForm(123);
      form.formData.value.comment = 'a'.repeat(2001); // Too long

      form.validateField('comment');

      expect(form.errors.value.comment).toBe('valuation.errors.commentTooLong');
    });
  });

  describe('Form Validation', () => {
    it('fails validation when value is missing', () => {
      const form = useValuationForm(123);
      form.formData.value.value = null;

      const isValid = form.validateForm();

      expect(isValid).toBe(false);
      expect(form.errors.value.value).toBe('valuation.errors.required');
    });

    it('fails validation when value is too low', () => {
      const form = useValuationForm(123);
      form.formData.value.value = 0;

      const isValid = form.validateForm();

      expect(isValid).toBe(false);
      expect(form.errors.value.value).toBe('valuation.errors.min');
    });

    it('fails validation when value is too high', () => {
      const form = useValuationForm(123);
      form.formData.value.value = 1000000;

      const isValid = form.validateForm();

      expect(isValid).toBe(false);
      expect(form.errors.value.value).toBe('valuation.errors.max');
    });

    it('passes validation with valid value', () => {
      const form = useValuationForm(123);
      form.formData.value.value = 5000;

      const isValid = form.validateForm();

      expect(isValid).toBe(true);
      expect(form.errors.value.value).toBeUndefined();
    });

    it('updates isFormValid computed property', () => {
      const form = useValuationForm(123);

      expect(form.isFormValid.value).toBe(false);

      form.formData.value.value = 5000;

      expect(form.isFormValid.value).toBe(true);
    });

    it('updates canSubmit computed property', () => {
      const form = useValuationForm(123);

      expect(form.canSubmit.value).toBe(false);

      form.formData.value.value = 5000;

      expect(form.canSubmit.value).toBe(true);
    });

    it('disables canSubmit when isSubmitting is true', async () => {
      const form = useValuationForm(123);
      form.formData.value.value = 5000;

      expect(form.canSubmit.value).toBe(true);

      form.isSubmitting.value = true;

      expect(form.canSubmit.value).toBe(false);
    });
  });

  describe('Form Reset', () => {
    it('resets form data to initial state', () => {
      const form = useValuationForm(123);
      form.formData.value.value = 5000;
      form.formData.value.comment = 'test comment';

      form.resetForm();

      expect(form.formData.value.value).toBe(null);
      expect(form.formData.value.comment).toBe('');
    });

    it('clears all errors', () => {
      const form = useValuationForm(123);
      form.errors.value.value = 'error message';
      form.errors.value.general = 'general error';

      form.resetForm();

      expect(Object.keys(form.errors.value).length).toBe(0);
    });

    it('clears touched fields', () => {
      const form = useValuationForm(123);
      form.touchedFields.value.add('value');
      form.touchedFields.value.add('comment');

      form.resetForm();

      expect(form.touchedFields.value.size).toBe(0);
    });
  });

  describe('Form Submission - Success', () => {
    it('returns null when form validation fails', async () => {
      const form = useValuationForm(123);
      form.formData.value.value = null; // Invalid

      const result = await form.handleSubmit();

      expect(result).toBeNull();
    });

    it('sets isSubmitting during submission', async () => {
      const form = useValuationForm(123);
      form.formData.value.value = 5000;

      vi.mocked(apiClient.post).mockResolvedValueOnce({
        data: {
          id: 1,
          value: 5000,
          currency: 'PLN',
          createdAt: '2025-01-01T00:00:00Z',
        },
      });

      const submitPromise = form.handleSubmit();

      expect(form.isSubmitting.value).toBe(true);

      await submitPromise;
    });

    it('clears isSubmitting after submission', async () => {
      const form = useValuationForm(123);
      form.formData.value.value = 5000;

      vi.mocked(apiClient.post).mockResolvedValueOnce({
        data: {
          id: 1,
          value: 5000,
          currency: 'PLN',
          createdAt: '2025-01-01T00:00:00Z',
        },
      });

      await form.handleSubmit();

      expect(form.isSubmitting.value).toBe(false);
    });

    it('calls API with correct endpoint', async () => {
      const bricksetId = 456;
      const form = useValuationForm(bricksetId);
      form.formData.value.value = 5000;

      vi.mocked(apiClient.post).mockResolvedValueOnce({
        data: { id: 1, value: 5000, currency: 'PLN', createdAt: '2025-01-01T00:00:00Z' },
      });

      await form.handleSubmit();

      expect(apiClient.post).toHaveBeenCalledWith(
        `/v1/bricksets/${bricksetId}/valuations`,
        expect.any(Object),
        expect.any(Object)
      );
    });

    it('sends request with credentials', async () => {
      const form = useValuationForm(123);
      form.formData.value.value = 5000;

      vi.mocked(apiClient.post).mockResolvedValueOnce({
        data: { id: 1, value: 5000, currency: 'PLN', createdAt: '2025-01-01T00:00:00Z' },
      });

      await form.handleSubmit();

      expect(apiClient.post).toHaveBeenCalledWith(
        expect.any(String),
        expect.any(Object),
        expect.objectContaining({ withCredentials: true })
      );
    });

    it('converts form data to API request format', async () => {
      const form = useValuationForm(123);
      form.formData.value.value = 5000;
      form.formData.value.comment = 'Nice bricks';

      vi.mocked(apiClient.post).mockResolvedValueOnce({
        data: { id: 1, value: 5000, currency: 'PLN', createdAt: '2025-01-01T00:00:00Z' },
      });

      await form.handleSubmit();

      expect(apiClient.post).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          value: 5000,
          currency: 'PLN',
          comment: 'Nice bricks',
        }),
        expect.any(Object)
      );
    });

    it('omits undefined comment from request', async () => {
      const form = useValuationForm(123);
      form.formData.value.value = 5000;
      form.formData.value.comment = ''; // Empty comment

      vi.mocked(apiClient.post).mockResolvedValueOnce({
        data: { id: 1, value: 5000, currency: 'PLN', createdAt: '2025-01-01T00:00:00Z' },
      });

      await form.handleSubmit();

      expect(apiClient.post).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          value: 5000,
          currency: 'PLN',
          comment: undefined,
        }),
        expect.any(Object)
      );
    });

    it('returns API response on success', async () => {
      const form = useValuationForm(123);
      form.formData.value.value = 5000;

      const mockResponse = {
        id: 1,
        value: 5000,
        currency: 'PLN',
        createdAt: '2025-01-01T00:00:00Z',
      };

      vi.mocked(apiClient.post).mockResolvedValueOnce({ data: mockResponse });

      const result = await form.handleSubmit();

      expect(result).toEqual(mockResponse);
    });
  });

  describe('Form Submission - Error Handling', () => {
    it('handles 400 validation error from API', async () => {
      const form = useValuationForm(123);
      form.formData.value.value = 5000;

      const mockError = {
        response: {
          status: 400,
          data: {
            errors: {
              value: ['Value must be a positive number'],
            },
          },
        },
      };

      vi.mocked(apiClient.post).mockRejectedValueOnce(mockError);

      let thrownError;
      try {
        await form.handleSubmit();
      } catch (error) {
        thrownError = error;
      }

      expect(thrownError).toBeInstanceOf(ValuationValidationError);
      expect(form.errors.value.value).toBe('Value must be a positive number');
    });

    it('handles 409 duplicate valuation error', async () => {
      const form = useValuationForm(123);
      form.formData.value.value = 5000;

      const mockError = {
        response: {
          status: 409,
          data: {},
        },
      };

      vi.mocked(apiClient.post).mockRejectedValueOnce(mockError);

      let thrownError;
      try {
        await form.handleSubmit();
      } catch (error) {
        thrownError = error;
      }

      expect(thrownError).toBeInstanceOf(ValuationDuplicateError);
      expect(form.errors.value.general).toBe('valuation.errors.duplicate');
    });

    it('handles 401 unauthorized error', async () => {
      const form = useValuationForm(123);
      form.formData.value.value = 5000;

      const mockError = {
        response: {
          status: 401,
          data: {},
        },
      };

      vi.mocked(apiClient.post).mockRejectedValueOnce(mockError);

      let thrownError;
      try {
        await form.handleSubmit();
      } catch (error) {
        thrownError = error;
      }

      expect(thrownError).toBeInstanceOf(Error);
      expect(form.errors.value.general).toBe('errors.unauthorized');
    });

    it('handles 404 not found error', async () => {
      const form = useValuationForm(123);
      form.formData.value.value = 5000;

      const mockError = {
        response: {
          status: 404,
          data: {},
        },
      };

      vi.mocked(apiClient.post).mockRejectedValueOnce(mockError);

      let thrownError;
      try {
        await form.handleSubmit();
      } catch (error) {
        thrownError = error;
      }

      expect(thrownError).toBeInstanceOf(Error);
      expect(form.errors.value.general).toBe('valuation.errors.notFound');
    });

    it('handles 500+ server error', async () => {
      const form = useValuationForm(123);
      form.formData.value.value = 5000;

      const mockError = {
        response: {
          status: 500,
          data: {},
        },
      };

      vi.mocked(apiClient.post).mockRejectedValueOnce(mockError);

      let thrownError;
      try {
        await form.handleSubmit();
      } catch (error) {
        thrownError = error;
      }

      expect(thrownError).toBeInstanceOf(Error);
      expect(form.errors.value.general).toBe('valuation.errors.serverError');
    });

    it('handles non-Axios network error', async () => {
      const form = useValuationForm(123);
      form.formData.value.value = 5000;

      vi.mocked(apiClient.post).mockRejectedValueOnce(new Error('Network error'));

      let thrownError;
      try {
        await form.handleSubmit();
      } catch (error) {
        thrownError = error;
      }

      expect(thrownError).toBeInstanceOf(Error);
      expect(form.errors.value.general).toBe('valuation.errors.networkError');
    });

    it('sets isSubmitting to false on error', async () => {
      const form = useValuationForm(123);
      form.formData.value.value = 5000;

      const mockError = {
        response: {
          status: 500,
          data: {},
        },
      };

      vi.mocked(apiClient.post).mockRejectedValueOnce(mockError);

      try {
        await form.handleSubmit();
      } catch {
        // Handle error
      }

      expect(form.isSubmitting.value).toBe(false);
    });
  });
});
