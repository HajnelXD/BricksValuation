/**
 * Composable: useRegisterForm
 * Encapsulates registration form validation and submission logic
 */

import { reactive, computed } from 'vue';
import type { RegisterFormData, FieldErrors } from '@/types/auth';

// Validation regex patterns
const USERNAME_REGEX = /^[A-Za-z0-9._-]+$/;
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function useRegisterForm() {
  const formData = reactive<RegisterFormData>({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  });

  const fieldErrors = reactive<FieldErrors>({});

  const setFieldError = (field: keyof FieldErrors, message: string): void => {
    fieldErrors[field] = message;
  };

  const clearFieldErrorValue = (field: keyof FieldErrors): void => {
    delete fieldErrors[field];
  };

  /**
   * Validate username field
   */
  function validateUsername(): boolean {
    const username = formData.username.trim();
    formData.username = username;

    if (!username) {
      setFieldError('username', 'register.errors.usernameRequired');
      return false;
    }

    if (username.length < 3 || username.length > 50) {
      setFieldError('username', 'register.errors.usernameLength');
      return false;
    }

    if (!USERNAME_REGEX.test(username)) {
      setFieldError('username', 'register.errors.usernameFormat');
      return false;
    }

    // Success - remove username error
    clearFieldErrorValue('username');
    return true;
  }

  /**
   * Validate email field
   */
  function validateEmail(): boolean {
    const email = formData.email.trim();
    formData.email = email;

    if (!email) {
      setFieldError('email', 'register.errors.emailRequired');
      return false;
    }

    if (!EMAIL_REGEX.test(email)) {
      setFieldError('email', 'register.errors.emailFormat');
      return false;
    }

    // Success - remove email error
    clearFieldErrorValue('email');
    return true;
  }

  /**
   * Validate password field
   */
  function validatePassword(): boolean {
    const password = formData.password;

    if (!password) {
      setFieldError('password', 'register.errors.passwordRequired');
      return false;
    }

    if (password.length < 8) {
      setFieldError('password', 'register.errors.passwordLength');
      return false;
    }

    // Success - remove password error
    clearFieldErrorValue('password');
    return true;
  }

  /**
   * Validate password confirmation field
   */
  function validateConfirmPassword(): boolean {
    const confirmPassword = formData.confirmPassword;

    if (!confirmPassword) {
      setFieldError('confirmPassword', 'register.errors.confirmPasswordRequired');
      return false;
    }

    if (confirmPassword !== formData.password) {
      setFieldError('confirmPassword', 'register.errors.passwordsNotMatch');
      return false;
    }

    // Success - remove confirmPassword error
    clearFieldErrorValue('confirmPassword');
    return true;
  }

  /**
   * Validate single field by name
   */
  function validateField(fieldName: keyof RegisterFormData): boolean {
    switch (fieldName) {
      case 'username':
        return validateUsername();
      case 'email':
        return validateEmail();
      case 'password':
        return validatePassword();
      case 'confirmPassword':
        return validateConfirmPassword();
      default:
        return true;
    }
  }

  /**
   * Validate entire form
   */
  function validateForm(): boolean {
    const usernameValid = validateUsername();
    const emailValid = validateEmail();
    const passwordValid = validatePassword();
    const confirmPasswordValid = validateConfirmPassword();

    return usernameValid && emailValid && passwordValid && confirmPasswordValid;
  }

  /**
   * Clear error for a specific field
   */
  function clearFieldError(fieldName: keyof FieldErrors | keyof RegisterFormData | string): void {
    clearFieldErrorValue(fieldName as keyof FieldErrors);
  }

  /**
   * Check if form has any errors
   */
  const hasErrors = computed(() => Object.keys(fieldErrors).length > 0);

  return {
    formData,
    fieldErrors,
    hasErrors,
    validateField,
    validateForm,
    clearFieldError,
  };
}
