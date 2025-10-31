/**
 * useBrickSetForm Composable
 * Manages BrickSet create/edit form state, validation, and submission
 *
 * Features:
 * - Form data state management with reactive updates
 * - Per-field validation with error messages
 * - Full form validation before submission
 * - API integration with error handling
 * - Support for duplicate detection (409 Conflict)
 * - Form dirty state tracking
 * - Error mapping from API responses to field errors
 */

import { reactive, ref, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import apiClient from '@/config/axios';
import { env } from '@/config/env';
import type {
  BrickSetFormData,
  FieldErrors,
  CreateBrickSetRequest,
  CreateBrickSetResponse,
  BrickSetValidationError,
  DuplicateSetInfo,
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
export class ValidationError extends Error {
  constructor(public errors: Record<string, string[]>) {
    super('Validation failed');
    this.name = 'ValidationError';
  }
}

/**
 * Custom error class for duplicate set errors
 */
export class DuplicateError extends Error {
  constructor(
    message: string,
    public constraint: string,
    public duplicateInfo?: DuplicateSetInfo
  ) {
    super(message);
    this.name = 'DuplicateError';
  }
}

/**
 * Validation rules for each field
 */
const VALIDATION_RULES = {
  number: {
    required: true,
    minValue: 0,
    maxValue: 9999999,
    pattern: /^\d+$/,
  },
  ownerInitialEstimate: {
    required: false,
    minValue: 1,
    maxValue: 999999,
    pattern: /^\d+$/,
  },
};

export function useBrickSetForm() {
  const { t } = useI18n();

  // Form state
  const formData = reactive<BrickSetFormData>({
    number: '',
    productionStatus: 'ACTIVE',
    completeness: 'COMPLETE',
    hasInstructions: false,
    hasBox: false,
    isFactorySealed: false,
    ownerInitialEstimate: null,
    isDirty: false,
  });

  // Error state
  const fieldErrors = reactive<FieldErrors>({});
  const isSubmitting = ref(false);
  const duplicateSetInfo = ref<DuplicateSetInfo | null>(null);

  // Computed properties
  const hasErrors = computed(() => Object.keys(fieldErrors).length > 0);
  const isDirty = computed(() => formData.isDirty);

  /**
   * Validate individual field
   */
  function validateField(fieldName: keyof BrickSetFormData): boolean {
    // Clear previous error for this field
    delete fieldErrors[fieldName as keyof FieldErrors];

    const value = formData[fieldName];

    switch (fieldName) {
      case 'number': {
        const numValue = formData.number.trim();
        if (!numValue) {
          fieldErrors.number = t('bricksets.create.errors.numberRequired');
          return false;
        }
        if (!VALIDATION_RULES.number.pattern.test(numValue)) {
          fieldErrors.number = t('bricksets.create.errors.numberFormat');
          return false;
        }
        const num = parseInt(numValue, 10);
        if (num < VALIDATION_RULES.number.minValue || num > VALIDATION_RULES.number.maxValue) {
          fieldErrors.number = t('bricksets.create.errors.numberRange');
          return false;
        }
        return true;
      }

      case 'productionStatus': {
        if (!value || value === '') {
          fieldErrors.productionStatus = t('bricksets.create.errors.productionStatusRequired');
          return false;
        }
        if (value !== 'ACTIVE' && value !== 'RETIRED') {
          fieldErrors.productionStatus = t('bricksets.create.errors.productionStatusInvalid');
          return false;
        }
        return true;
      }

      case 'completeness': {
        if (!value || value === '') {
          fieldErrors.completeness = t('bricksets.create.errors.completenessRequired');
          return false;
        }
        if (value !== 'COMPLETE' && value !== 'INCOMPLETE') {
          fieldErrors.completeness = t('bricksets.create.errors.completenessInvalid');
          return false;
        }
        return true;
      }

      case 'ownerInitialEstimate': {
        // Optional field
        if (value === null || value === '') {
          return true;
        }
        const strValue = value.toString().trim();
        if (!VALIDATION_RULES.ownerInitialEstimate.pattern.test(strValue)) {
          fieldErrors.ownerInitialEstimate = t('bricksets.create.errors.estimateFormat');
          return false;
        }
        const num = parseInt(strValue, 10);
        if (
          num < VALIDATION_RULES.ownerInitialEstimate.minValue ||
          num > VALIDATION_RULES.ownerInitialEstimate.maxValue
        ) {
          fieldErrors.ownerInitialEstimate = t('bricksets.create.errors.estimateRange');
          return false;
        }
        return true;
      }

      // Boolean fields are always valid
      case 'hasInstructions':
      case 'hasBox':
      case 'isFactorySealed':
        return true;

      default:
        return true;
    }
  }

  /**
   * Validate entire form
   */
  function validateForm(): boolean {
    const fieldNames: (keyof BrickSetFormData)[] = [
      'number',
      'productionStatus',
      'completeness',
      'ownerInitialEstimate',
    ];

    let isValid = true;
    for (const fieldName of fieldNames) {
      if (!validateField(fieldName)) {
        isValid = false;
      }
    }

    return isValid;
  }

  /**
   * Set value for a field and mark form as dirty
   */
  function setFieldValue(fieldName: keyof BrickSetFormData, value: string | boolean | null) {
    formData[fieldName] = value;
    formData.isDirty = true;

    // Clear field error when user starts typing
    if (fieldErrors[fieldName as keyof FieldErrors]) {
      delete fieldErrors[fieldName as keyof FieldErrors];
    }
  }

  /**
   * Reset form to initial state
   */
  function resetForm() {
    formData.number = '';
    formData.productionStatus = 'ACTIVE';
    formData.completeness = 'COMPLETE';
    formData.hasInstructions = false;
    formData.hasBox = false;
    formData.isFactorySealed = false;
    formData.ownerInitialEstimate = null;
    formData.isDirty = false;
    duplicateSetInfo.value = null;

    Object.keys(fieldErrors).forEach((key) => {
      delete fieldErrors[key as keyof FieldErrors];
    });
  }

  /**
   * Map API validation error response to form field errors
   */
  function mapApiErrorsToForm(apiError: BrickSetValidationError): void {
    // Map snake_case API field names to camelCase form field names
    const fieldNameMap: Record<string, keyof FieldErrors> = {
      number: 'number',
      production_status: 'productionStatus',
      completeness: 'completeness',
      has_instructions: 'hasInstructions',
      has_box: 'hasBox',
      is_factory_sealed: 'isFactorySealed',
      owner_initial_estimate: 'ownerInitialEstimate',
    };

    Object.entries(apiError.errors).forEach(([apiFieldName, messages]) => {
      const formFieldName = fieldNameMap[apiFieldName];
      if (formFieldName && messages && messages.length > 0) {
        fieldErrors[formFieldName] = messages[0];
      }
    });
  }

  /**
   * Convert form data to API request format
   */
  function convertFormDataToRequest(): CreateBrickSetRequest {
    return {
      number: parseInt(formData.number, 10),
      production_status: formData.productionStatus,
      completeness: formData.completeness,
      has_instructions: formData.hasInstructions,
      has_box: formData.hasBox,
      is_factory_sealed: formData.isFactorySealed,
      owner_initial_estimate: formData.ownerInitialEstimate
        ? parseInt(formData.ownerInitialEstimate, 10)
        : null,
    };
  }

  /**
   * Submit form - validate and call API
   */
  async function submitForm(): Promise<CreateBrickSetResponse> {
    // Client-side validation
    if (!validateForm()) {
      throw new Error('Form validation failed');
    }

    isSubmitting.value = true;

    try {
      const request = convertFormDataToRequest();

      const response = (await apiClient.post(`${API_BASE_URL}`, request, {
        withCredentials: true,
      })) as { data: CreateBrickSetResponse };

      return response.data;
    } catch (err: unknown) {
      // Handle different error types
      if (!isAxiosErrorLike(err)) {
        throw err;
      }

      const status = err.response?.status;
      const data = err.response?.data;

      // 400 - Validation error
      if (status === 400 && typeof data === 'object' && data !== null && 'errors' in data) {
        const validationError = new ValidationError(
          (data as Record<string, unknown>).errors as Record<string, string[]>
        );
        mapApiErrorsToForm(data as BrickSetValidationError);
        throw validationError;
      }

      // 409 - Duplicate set
      if (status === 409 && typeof data === 'object' && data !== null) {
        const duplicateData = data as Record<string, unknown>;

        // Store duplicate info for modal display
        duplicateSetInfo.value = {
          setId: 0, // Will be populated by parent component via search
          setNumber: parseInt(formData.number, 10),
          productionStatus: formData.productionStatus,
          completeness: formData.completeness,
          hasInstructions: formData.hasInstructions,
          hasBox: formData.hasBox,
          isFactorySealed: formData.isFactorySealed,
          ownerName: '', // Not available from error response
        };

        const duplicateError = new DuplicateError(
          (duplicateData.detail as string) || t('bricksets.create.errors.duplicate'),
          (duplicateData.constraint as string) || 'brickset_global_identity',
          duplicateSetInfo.value
        );
        throw duplicateError;
      }

      // 401 - Unauthorized
      if (status === 401) {
        throw new Error(t('errors.unauthorized'));
      }

      // 500+ - Server error
      if (status && status >= 500) {
        throw new Error(t('errors.serverError'));
      }

      throw new Error(t('errors.networkError'));
    } finally {
      isSubmitting.value = false;
    }
  }

  return {
    // State
    formData,
    fieldErrors,
    isSubmitting,
    duplicateSetInfo,

    // Computed
    hasErrors,
    isDirty,

    // Methods
    validateField,
    validateForm,
    setFieldValue,
    resetForm,
    submitForm,
    mapApiErrorsToForm,
  };
}
