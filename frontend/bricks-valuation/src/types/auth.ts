/**
 * Authentication Types
 * DTO types from API and internal ViewModel types for UI layer
 */

// DTO - Data Transfer Objects from API

/**
 * User DTO - returned after login or profile fetch
 */
export interface UserDTO {
  id: number;
  username: string;
  email: string;
  created_at?: string; // ISO 8601 datetime
}

/**
 * Request payload for user login
 */
export interface LoginRequestDTO {
  username: string; // accepts username or email
  password: string;
}

/**
 * Response payload for successful login (200 OK)
 */
export interface LoginResponseDTO {
  user: UserDTO;
  token?: string; // optional in body (mainly HttpOnly cookie)
}

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
  message?: string;
}

/**
 * Response payload for invalid credentials error (401 Unauthorized)
 */
export interface InvalidCredentialsErrorDTO {
  error_code: 'INVALID_CREDENTIALS';
  message: string; // "Nieprawidłowe dane logowania"
}

/**
 * Response payload for not authenticated error (401 Unauthorized)
 */
export interface NotAuthenticatedErrorDTO {
  error_code: 'NOT_AUTHENTICATED';
  message: string;
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
 * Form data state for login form
 */
export interface LoginFormData {
  username: string;
  password: string;
}

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
