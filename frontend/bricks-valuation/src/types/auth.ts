/**
 * Authentication Types
 * DTO types from API and internal ViewModel types for UI layer
 */

// DTO - Data Transfer Objects from API

/**
 * Request payload for user registration
 */
export interface RegisterRequestDTO {
  username: string;
  email: string;
  password: string;
}

/**
 * Response payload for successful registration (201 Created)
 */
export interface RegisterResponseDTO {
  id: number;
  username: string;
  email: string;
  created_at: string; // ISO 8601 timestamp
}

/**
 * Response payload for validation errors (400 Bad Request)
 */
export interface ValidationErrorDTO {
  errors: {
    [field: string]: string[];
  };
  code: 'VALIDATION_ERROR';
}

/**
 * Response payload for conflict errors (409 Conflict)
 */
export interface ConflictErrorDTO {
  detail: string;
  code: 'USERNAME_TAKEN' | 'EMAIL_TAKEN';
}

// ViewModel - Internal representation for UI layer

/**
 * Form data state for registration form
 */
export interface RegisterFormData {
  username: string;
  email: string;
  password: string;
  confirmPassword: string; // Not sent to API, only for client-side validation
}

/**
 * Field errors state for validation messages
 */
export interface FieldErrors {
  username?: string;
  email?: string;
  password?: string;
  confirmPassword?: string;
}

/**
 * Password strength requirements
 */
export interface PasswordRequirement {
  label: string;
  satisfied: boolean;
}
