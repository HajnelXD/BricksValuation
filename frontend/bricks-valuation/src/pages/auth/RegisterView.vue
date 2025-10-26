<script setup lang="ts">
/**
 * RegisterView
 * Main registration view component
 * Manages form state, validation, API calls, and error handling
 * Uses Composition API with setup syntax
 */

import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { useRegisterForm } from '@/composables/useRegisterForm';
import { useAuthStore } from '@/stores/auth';
import type {
  ValidationErrorDTO,
  ConflictErrorDTO,
  RegisterFormData,
  FieldErrors,
} from '@/types/auth';
import AuthFormLayout from '@/components/auth/AuthFormLayout.vue';
import BaseInput from '@/components/auth/BaseInput.vue';

const router = useRouter();
const { t } = useI18n();
const authStore = useAuthStore();

// Form state and validation
const { formData, fieldErrors, hasErrors, validateField, validateForm, clearFieldError } =
  useRegisterForm();
const isSubmitting = ref(false);
const serverError = ref<string | null>(null);

// Computed properties
const isSubmitDisabled = computed(() => hasErrors.value || isSubmitting.value);

/**
 * Handle form submission
 */
async function handleSubmit(): Promise<void> {
  // Clear previous server errors
  serverError.value = null;

  // Validate entire form
  if (!validateForm()) {
    return;
  }

  isSubmitting.value = true;

  try {
    // Prepare request data (without confirmPassword)
    const requestData = {
      username: formData.username.trim(),
      email: formData.email.trim(),
      password: formData.password,
    };

    // Call API
    await authStore.register(requestData);

    // Success - show message and redirect
    // Note: In a real app, you'd use a toast notification here
    await router.push({ name: 'login' });
  } catch (error: unknown) {
    handleRegistrationError(error as Error & { response?: { status: number; data: unknown } });
  } finally {
    isSubmitting.value = false;
  }
}

/**
 * Handle registration errors
 */
function handleRegistrationError(
  error: Error & { response?: { status: number; data: unknown } }
): void {
  const status = error.response?.status;
  const data = error.response?.data;

  if (status === 400) {
    // Validation error - map to fields
    handleValidationError(data as ValidationErrorDTO);
  } else if (status === 409) {
    // Conflict error - username or email taken
    handleConflictError(data as ConflictErrorDTO);
  } else if (status && status >= 500) {
    // Server error
    serverError.value = t('errors.serverError');
  } else if (!error.response) {
    // Network error
    serverError.value = t('errors.networkError');
  } else {
    // Other errors
    serverError.value = t('errors.serverError');
  }
}

/**
 * Handle validation error (400)
 */
function handleValidationError(data: ValidationErrorDTO): void {
  if (data.errors) {
    Object.entries(data.errors).forEach(([field, messages]) => {
      if (messages && messages.length > 0) {
        fieldErrors[field as keyof FieldErrors] = messages[0];
      }
    });
  }
}

/**
 * Handle conflict error (409)
 */
function handleConflictError(data: ConflictErrorDTO): void {
  if (data.code === 'USERNAME_TAKEN') {
    fieldErrors.username = t('register.errors.usernameTaken');
  } else if (data.code === 'EMAIL_TAKEN') {
    fieldErrors.email = t('register.errors.emailTaken');
  }
}

/**
 * Handle field blur - validate single field
 */
function handleFieldBlur(fieldName: keyof RegisterFormData): void {
  validateField(fieldName);
}

/**
 * Handle field input - clear error
 */
function handleFieldInput(fieldName: keyof RegisterFormData): void {
  clearFieldError(fieldName);
}
</script>

<template>
  <AuthFormLayout :title="$t('register.title')">
    <!-- Form -->
    <form class="space-y-4 sm:space-y-5" novalidate @submit.prevent="handleSubmit">
      <!-- Server Error Alert -->
      <div
        v-if="serverError"
        class="p-4 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-700 rounded-lg animate-in fade-in duration-200"
        role="alert"
      >
        <div class="flex items-start gap-3">
          <span class="flex-shrink-0 text-lg">⚠️</span>
          <p class="text-sm text-red-700 dark:text-red-200">{{ serverError }}</p>
        </div>
      </div>

      <!-- Username Field -->
      <BaseInput
        v-model="formData.username"
        :label="$t('register.username')"
        type="text"
        :error="fieldErrors.username ? $t(fieldErrors.username) : undefined"
        :placeholder="$t('register.username')"
        :disabled="isSubmitting"
        autocomplete="username"
        @blur="handleFieldBlur('username')"
        @input="handleFieldInput('username')"
      />

      <!-- Email Field -->
      <BaseInput
        v-model="formData.email"
        :label="$t('register.email')"
        type="email"
        :error="fieldErrors.email ? $t(fieldErrors.email) : undefined"
        :placeholder="$t('register.email')"
        :disabled="isSubmitting"
        autocomplete="email"
        @blur="handleFieldBlur('email')"
        @input="handleFieldInput('email')"
      />

      <!-- Password Field -->
      <BaseInput
        v-model="formData.password"
        :label="$t('register.password')"
        type="password"
        :error="fieldErrors.password ? $t(fieldErrors.password) : undefined"
        :placeholder="$t('register.password')"
        :disabled="isSubmitting"
        autocomplete="new-password"
        @blur="handleFieldBlur('password')"
        @input="handleFieldInput('password')"
      />

      <!-- Confirm Password Field -->
      <BaseInput
        v-model="formData.confirmPassword"
        :label="$t('register.confirmPassword')"
        type="password"
        :error="fieldErrors.confirmPassword ? $t(fieldErrors.confirmPassword) : undefined"
        :placeholder="$t('register.confirmPassword')"
        :disabled="isSubmitting"
        autocomplete="new-password"
        @blur="handleFieldBlur('confirmPassword')"
        @input="handleFieldInput('confirmPassword')"
      />

      <!-- Submit Button -->
      <button
        type="submit"
        :disabled="isSubmitDisabled"
        :class="[
          'w-full py-2.5 sm:py-3 px-4 rounded-lg font-semibold text-white transition-all duration-200',
          'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500',
          'disabled:focus:ring-offset-0',
          'text-sm sm:text-base',
          isSubmitDisabled
            ? 'bg-gray-400 dark:bg-gray-600 cursor-not-allowed opacity-60'
            : 'bg-blue-600 dark:bg-blue-700 hover:bg-blue-700 dark:hover:bg-blue-600 active:bg-blue-800 dark:active:bg-blue-800',
        ]"
      >
        <span v-if="!isSubmitting" class="flex items-center justify-center gap-2">
          {{ $t('register.submit') }}
        </span>
        <span v-else class="flex items-center justify-center gap-2">
          <svg
            class="w-4 h-4 animate-spin"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <circle
              class="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              stroke-width="4"
            />
            <path
              class="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
          <span class="hidden sm:inline">{{ $t('register.submit') }}</span>
        </span>
      </button>
    </form>

    <!-- Links to Login -->
    <template #links>
      <p class="text-sm">
        {{ $t('register.hasAccount') }}
        <RouterLink
          :to="{ name: 'login' }"
          class="font-semibold text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 hover:underline transition-colors"
        >
          {{ $t('register.login') }}
        </RouterLink>
      </p>
    </template>
  </AuthFormLayout>
</template>

<style scoped>
/* No additional scoped styles needed - using Tailwind CSS */
</style>
