/**
 * Tests for useRegisterForm composable
 * Tests validation logic for all form fields
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { useRegisterForm } from '@/composables/useRegisterForm';

describe('useRegisterForm composable', () => {
  let form: ReturnType<typeof useRegisterForm>;

  beforeEach(() => {
    form = useRegisterForm();
  });

  // ========== Username Validation Tests ==========

  describe('validateUsername', () => {
    it('should fail when username is empty', () => {
      form.formData.username = '';
      const result = form.validateField('username');
      expect(result).toBe(false);
      expect(form.fieldErrors.username).toBe('register.errors.usernameRequired');
    });

    it('should fail when username is too short (< 3 chars)', () => {
      form.formData.username = 'ab';
      const result = form.validateField('username');
      expect(result).toBe(false);
      expect(form.fieldErrors.username).toBe('register.errors.usernameLength');
    });

    it('should fail when username is too long (> 50 chars)', () => {
      form.formData.username = 'a'.repeat(51);
      const result = form.validateField('username');
      expect(result).toBe(false);
      expect(form.fieldErrors.username).toBe('register.errors.usernameLength');
    });

    it('should fail when username contains invalid characters', () => {
      form.formData.username = 'user@name';
      const result = form.validateField('username');
      expect(result).toBe(false);
      expect(form.fieldErrors.username).toBe('register.errors.usernameFormat');
    });

    it('should pass with valid username (alphanumeric with dots, underscores, dashes)', () => {
      form.formData.username = 'valid_user.name-123';
      const result = form.validateField('username');
      expect(result).toBe(true);
      expect(form.fieldErrors.username).toBeUndefined();
    });

    it('should pass with valid username at minimum length', () => {
      form.formData.username = 'abc';
      const result = form.validateField('username');
      expect(result).toBe(true);
      expect(form.fieldErrors.username).toBeUndefined();
    });

    it('should pass with valid username at maximum length', () => {
      form.formData.username = 'a'.repeat(50);
      const result = form.validateField('username');
      expect(result).toBe(true);
      expect(form.fieldErrors.username).toBeUndefined();
    });

    it('should trim whitespace from username', () => {
      form.formData.username = '  valid_user  ';
      const result = form.validateField('username');
      expect(result).toBe(true);
    });
  });

  // ========== Email Validation Tests ==========

  describe('validateEmail', () => {
    it('should fail when email is empty', () => {
      form.formData.email = '';
      const result = form.validateField('email');
      expect(result).toBe(false);
      expect(form.fieldErrors.email).toBe('register.errors.emailRequired');
    });

    it('should fail when email format is invalid (missing @)', () => {
      form.formData.email = 'invalidemail.com';
      const result = form.validateField('email');
      expect(result).toBe(false);
      expect(form.fieldErrors.email).toBe('register.errors.emailFormat');
    });

    it('should fail when email format is invalid (missing domain)', () => {
      form.formData.email = 'invalid@';
      const result = form.validateField('email');
      expect(result).toBe(false);
      expect(form.fieldErrors.email).toBe('register.errors.emailFormat');
    });

    it('should fail when email format is invalid (missing TLD)', () => {
      form.formData.email = 'invalid@domain';
      const result = form.validateField('email');
      expect(result).toBe(false);
      expect(form.fieldErrors.email).toBe('register.errors.emailFormat');
    });

    it('should pass with valid email format', () => {
      form.formData.email = 'user@example.com';
      const result = form.validateField('email');
      expect(result).toBe(true);
      expect(form.fieldErrors.email).toBeUndefined();
    });

    it('should pass with valid email (multiple subdomains)', () => {
      form.formData.email = 'user@sub.example.co.uk';
      const result = form.validateField('email');
      expect(result).toBe(true);
      expect(form.fieldErrors.email).toBeUndefined();
    });

    it('should trim whitespace from email', () => {
      form.formData.email = '  user@example.com  ';
      const result = form.validateField('email');
      expect(result).toBe(true);
    });
  });

  // ========== Password Validation Tests ==========

  describe('validatePassword', () => {
    it('should fail when password is empty', () => {
      form.formData.password = '';
      const result = form.validateField('password');
      expect(result).toBe(false);
      expect(form.fieldErrors.password).toBe('register.errors.passwordRequired');
    });

    it('should fail when password is too short (< 8 chars)', () => {
      form.formData.password = 'pass123';
      const result = form.validateField('password');
      expect(result).toBe(false);
      expect(form.fieldErrors.password).toBe('register.errors.passwordLength');
    });

    it('should pass with valid password (exactly 8 chars)', () => {
      form.formData.password = 'password';
      const result = form.validateField('password');
      expect(result).toBe(true);
      expect(form.fieldErrors.password).toBeUndefined();
    });

    it('should pass with valid password (> 8 chars)', () => {
      form.formData.password = 'valid_password_123!@#';
      const result = form.validateField('password');
      expect(result).toBe(true);
      expect(form.fieldErrors.password).toBeUndefined();
    });
  });

  // ========== Confirm Password Validation Tests ==========

  describe('validateConfirmPassword', () => {
    it('should fail when confirmPassword is empty', () => {
      form.formData.password = 'password123';
      form.formData.confirmPassword = '';
      const result = form.validateField('confirmPassword');
      expect(result).toBe(false);
      expect(form.fieldErrors.confirmPassword).toBe('register.errors.confirmPasswordRequired');
    });

    it('should fail when passwords do not match', () => {
      form.formData.password = 'password123';
      form.formData.confirmPassword = 'password456';
      const result = form.validateField('confirmPassword');
      expect(result).toBe(false);
      expect(form.fieldErrors.confirmPassword).toBe('register.errors.passwordsNotMatch');
    });

    it('should pass when passwords match', () => {
      form.formData.password = 'password123';
      form.formData.confirmPassword = 'password123';
      const result = form.validateField('confirmPassword');
      expect(result).toBe(true);
      expect(form.fieldErrors.confirmPassword).toBeUndefined();
    });
  });

  // ========== validateForm Tests ==========

  describe('validateForm', () => {
    it('should fail when all fields are empty', () => {
      const result = form.validateForm();
      expect(result).toBe(false);
      const errorCount = Object.keys(form.fieldErrors).filter(
        (key) => !key.startsWith('_') && !key.startsWith('__')
      ).length;
      expect(errorCount).toBe(4);
    });

    it('should fail when any single field is invalid', () => {
      form.formData.username = 'valid_user';
      form.formData.email = 'user@example.com';
      form.formData.password = 'password123';
      form.formData.confirmPassword = 'different123';

      const result = form.validateForm();
      expect(result).toBe(false);
      expect(form.fieldErrors.confirmPassword).toBeDefined();
    });

    it('should pass when all fields are valid', () => {
      form.formData.username = 'valid_user';
      form.formData.email = 'user@example.com';
      form.formData.password = 'password123';
      form.formData.confirmPassword = 'password123';

      const result = form.validateForm();
      expect(result).toBe(true);
      const errorCount = Object.keys(form.fieldErrors).filter(
        (key) => !key.startsWith('_') && !key.startsWith('__')
      ).length;
      expect(errorCount).toBe(0);
    });
  });

  // ========== clearFieldError Tests ==========

  describe('clearFieldError', () => {
    it('should clear error for specified field', () => {
      // Fresh form for this test
      const testForm = useRegisterForm();
      testForm.fieldErrors.username = 'register.errors.usernameRequired';
      testForm.fieldErrors.email = 'register.errors.emailRequired';

      testForm.clearFieldError('username');

      // After clearing, username should be deleted
      expect('username' in testForm.fieldErrors).toBe(false);
      expect(testForm.fieldErrors.email).toBe('register.errors.emailRequired');
    });

    it('should not throw error when clearing non-existent error', () => {
      expect(() => {
        form.clearFieldError('username');
      }).not.toThrow();
    });
  });

  // ========== hasErrors computed property Tests ==========

  describe('hasErrors computed property', () => {
    it('should be true when there are field errors', () => {
      const testForm = useRegisterForm();
      testForm.fieldErrors.username = 'register.errors.usernameRequired';
      expect(testForm.hasErrors.value).toBe(true);
    });

    it('should be false when there are no errors', () => {
      const testForm = useRegisterForm();
      expect(testForm.hasErrors.value).toBe(false);
    });

    it('should be false on initialization', () => {
      const newForm = useRegisterForm();
      expect(newForm.hasErrors.value).toBe(false);
    });
  });
});
