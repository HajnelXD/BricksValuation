/**
 * useValuationForm Composable
 * Manages valuation form state, validation, and submission
 *
 * Features:
 * - Form data state management with reactive updates
 * - Per-field validation with error messages
 * - Full form validation before submission
 * - API integration with error handling
 * - Support for duplicate valuation detection (409 Conflict)
 * - Field touched tracking for conditional error display
 */

import { ref, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import apiClient from '@/config/axios';
import { env } from '@/config/env';
import type {
  ValuationFormData,
  ValuationValidationErrors,
  CreateValuationRequest,
  CreateValuationResponse,
} from '@/types/bricksets';

const API_BASE_URL = `/v${env.api.version}/bricksets`;

interface AxiosErrorLike {
  response?: {
    status?: number;
    data?: unknown;
  };
}

function isAxiosErrorLike(error: unknown): error is AxiosErrorLike {
  return typeof error === 'object' && error !== null && 'response' in error;
}

/**
 * Custom error class for validation errors
 */
export class ValuationValidationError extends Error {
  constructor(public errors: Record<string, string[]>) {
    super('Validation failed');
    this.name = 'ValuationValidationError';
  }
}

/**
 * Custom error class for duplicate valuation errors
 */
export class ValuationDuplicateError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ValuationDuplicateError';
  }
}

/**
 * Validation rules for valuation form fields
 */
const VALIDATION_RULES = {
  value: {
    required: true,
    minValue: 1,
    maxValue: 999999,
  },
  comment: {
    required: false,
    maxLength: 2000,
  },
};

export function useValuationForm(bricksetId: number) {
  const { t } = useI18n();

  // Form state
  const formData = ref<ValuationFormData>({
    value: null,
    comment: '',
  });

  // Error state
  const errors = ref<ValuationValidationErrors>({});
  const isSubmitting = ref(false);
  const touchedFields = ref<Set<string>>(new Set());

  // Computed properties
  const isFormValid = computed(() => {
    const valueError = validateValueField(formData.value.value);
    const commentError = validateCommentField(formData.value.comment);
    return !valueError && !commentError;
  });

  const canSubmit = computed(() => {
    return isFormValid.value && !isSubmitting.value;
  });

  /**
   * Validate value field
   * Returns error message or undefined if valid
   */
  function validateValueField(value: number | null): string | undefined {
    if (value === null || value === undefined) {
      return t('valuation.errors.required');
    }

    if (typeof value !== 'number' || isNaN(value)) {
      return t('valuation.errors.notNumber');
    }

    if (value < VALIDATION_RULES.value.minValue) {
      return t('valuation.errors.min');
    }

    if (value > VALIDATION_RULES.value.maxValue) {
      return t('valuation.errors.max');
    }

    return undefined;
  }

  /**
   * Validate comment field
   * Returns error message or undefined if valid
   */
  function validateCommentField(comment: string): string | undefined {
    if (comment.length > VALIDATION_RULES.comment.maxLength) {
      return t('valuation.errors.commentTooLong');
    }

    return undefined;
  }

  /**
   * Validate individual field and update error state
   */
  function validateField(fieldName: keyof ValuationFormData): void {
    // Clear previous error for this field
    delete errors.value[fieldName];

    const value = formData.value[fieldName];

    let errorMessage: string | undefined;

    if (fieldName === 'value') {
      errorMessage = validateValueField(value as number | null);
    } else if (fieldName === 'comment') {
      errorMessage = validateCommentField(value as string);
    }

    if (errorMessage) {
      errors.value[fieldName] = errorMessage;
    }
  }

  /**
   * Validate entire form
   */
  function validateForm(): boolean {
    // Only validate required 'value' field
    const valueError = validateValueField(formData.value.value);

    if (valueError) {
      errors.value.value = valueError;
      return false;
    }

    return true;
  }

  /**
   * Reset form to initial state
   */
  function resetForm(): void {
    formData.value = {
      value: null,
      comment: '',
    };
    errors.value = {};
    touchedFields.value.clear();
  }

  /**
   * Mark field as touched for conditional error display
   */
  function markFieldTouched(fieldName: string): void {
    touchedFields.value.add(fieldName);
  }

  /**
   * Convert form data to API request format
   */
  function convertFormDataToRequest(): CreateValuationRequest {
    return {
      value: formData.value.value!,
      currency: 'PLN',
      comment: formData.value.comment || undefined,
    };
  }

  /**
   * Submit form - validate and call API
   */
  async function handleSubmit(): Promise<CreateValuationResponse | null> {
    // Client-side validation
    if (!validateForm()) {
      return null;
    }

    isSubmitting.value = true;

    try {
      const request = convertFormDataToRequest();

      const response = (await apiClient.post(
        `${API_BASE_URL}/${bricksetId}/valuations`,
        request,
        {
          withCredentials: true,
        }
      )) as { data: CreateValuationResponse };

      return response.data;
    } catch (err: unknown) {
      // Handle different error types
      if (!isAxiosErrorLike(err)) {
        errors.value.general = t('valuation.errors.networkError');
        throw err;
      }

      const status = err.response?.status;
      const data = err.response?.data;

      // 400 - Validation error
      if (status === 400 && typeof data === 'object' && data !== null) {
        const errorData = data as Record<string, unknown>;
        if ('errors' in errorData) {
          // Map API errors to form fields
          const apiErrors = errorData.errors as Record<string, string[]>;
          Object.entries(apiErrors).forEach(([field, messages]) => {
            if (field === 'value' || field === 'comment') {
              errors.value[field as keyof ValuationValidationErrors] = messages[0];
            }
          });
        } else {
          errors.value.general = t('valuation.errors.serverError');
        }
        throw new ValuationValidationError(
          typeof errorData === 'object' && errorData !== null
            ? (errorData as Record<string, string[]>)
            : {}
        );
      }

      // 409 - Duplicate valuation
      if (status === 409) {
        errors.value.general = t('valuation.errors.duplicate');
        throw new ValuationDuplicateError(t('valuation.errors.duplicate'));
      }

      // 401 - Unauthorized
      if (status === 401) {
        errors.value.general = t('errors.unauthorized');
        throw new Error(t('errors.unauthorized'));
      }

      // 404 - Brickset not found
      if (status === 404) {
        errors.value.general = t('valuation.errors.notFound');
        throw new Error(t('valuation.errors.notFound'));
      }

      // 500+ - Server error
      if (status && status >= 500) {
        errors.value.general = t('valuation.errors.serverError');
        throw new Error(t('valuation.errors.serverError'));
      }

      errors.value.general = t('valuation.errors.networkError');
      throw new Error(t('valuation.errors.networkError'));
    } finally {
      isSubmitting.value = false;
    }
  }

  return {
    // State
    formData,
    errors,
    isSubmitting,
    touchedFields,

    // Computed
    isFormValid,
    canSubmit,

    // Methods
    validateField,
    validateForm,
    validateValueField,
    validateCommentField,
    resetForm,
    handleSubmit,
    markFieldTouched,
  };
}
