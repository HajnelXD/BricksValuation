/**
 * Form Helper Functions
 * Utilities for form data conversion and validation
 */

import type { BrickSetEditDetailDTO, BrickSetFormData, BrickSetUpdateDTO } from '@/types/bricksets';

/**
 * Convert BrickSetEditDetailDTO to BrickSetFormData
 * Maps API response (snake_case) to form data (camelCase)
 */
export function brickSetToFormData(brickSet: BrickSetEditDetailDTO): BrickSetFormData {
  return {
    number: brickSet.number.toString(),
    productionStatus: brickSet.production_status,
    completeness: brickSet.completeness,
    hasInstructions: brickSet.has_instructions,
    hasBox: brickSet.has_box,
    isFactorySealed: brickSet.is_factory_sealed,
    ownerInitialEstimate:
      brickSet.owner_initial_estimate !== null ? brickSet.owner_initial_estimate.toString() : null,
    isDirty: false,
  };
}

/**
 * Generate BrickSetUpdateDTO with only changed fields
 * Compares formData with originalData and returns partial update
 */
export function generateUpdateDTO(
  formData: BrickSetFormData,
  originalData: BrickSetFormData
): BrickSetUpdateDTO {
  const dto: BrickSetUpdateDTO = {};

  // Compare number (convert string to number)
  if (formData.number !== originalData.number) {
    const numberValue = parseInt(formData.number, 10);
    if (!isNaN(numberValue)) {
      dto.number = numberValue;
    }
  }

  // Compare production status
  if (formData.productionStatus !== originalData.productionStatus) {
    dto.production_status = formData.productionStatus;
  }

  // Compare completeness
  if (formData.completeness !== originalData.completeness) {
    dto.completeness = formData.completeness;
  }

  // Compare boolean fields
  if (formData.hasInstructions !== originalData.hasInstructions) {
    dto.has_instructions = formData.hasInstructions;
  }

  if (formData.hasBox !== originalData.hasBox) {
    dto.has_box = formData.hasBox;
  }

  if (formData.isFactorySealed !== originalData.isFactorySealed) {
    dto.is_factory_sealed = formData.isFactorySealed;
  }

  // Compare owner initial estimate (handle null and string conversion)
  if (formData.ownerInitialEstimate !== originalData.ownerInitialEstimate) {
    if (formData.ownerInitialEstimate === null || formData.ownerInitialEstimate === '') {
      dto.owner_initial_estimate = null;
    } else {
      const estimateValue = parseFloat(formData.ownerInitialEstimate);
      if (!isNaN(estimateValue)) {
        dto.owner_initial_estimate = estimateValue;
      }
    }
  }

  return dto;
}

/**
 * Validate set number field
 * @param value - Set number as string
 * @returns Error message or null if valid
 */
export function validateSetNumber(value: string): string | null {
  if (!value || value.trim() === '') {
    return 'To pole jest wymagane';
  }

  if (!/^\d{1,7}$/.test(value)) {
    return 'Numer zestawu może zawierać tylko cyfry (1-7 znaków)';
  }

  return null;
}

/**
 * Validate owner initial estimate field
 * @param value - Estimate value as string
 * @returns Error message or null if valid
 */
export function validateEstimate(value: string | null): string | null {
  // Field is optional
  if (value === null || value === '') {
    return null;
  }

  // Check if value contains only digits, optional decimal point, and optional minus sign
  if (!/^-?\d+(\.\d+)?$/.test(value)) {
    return 'Wartość musi być liczbą';
  }

  const num = parseFloat(value);

  if (isNaN(num)) {
    return 'Wartość musi być liczbą';
  }

  if (num <= 0) {
    return 'Wartość musi być większa od 0';
  }

  if (num >= 1000000) {
    return 'Wartość nie może przekraczać 999999';
  }

  return null;
}

/**
 * Deep clone form data for comparison
 * @param formData - Form data to clone
 * @returns Cloned form data
 */
export function cloneFormData(formData: BrickSetFormData): BrickSetFormData {
  return {
    ...formData,
    // Ensure deep copy for nested objects if needed in future
  };
}

/**
 * Check if two form data objects are equal
 * @param a - First form data
 * @param b - Second form data
 * @returns True if equal, false otherwise
 */
export function isFormDataEqual(a: BrickSetFormData, b: BrickSetFormData): boolean {
  return JSON.stringify(a) === JSON.stringify(b);
}
