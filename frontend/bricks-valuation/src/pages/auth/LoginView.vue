<script setup lang="ts">
/**
 * LoginView
 * User login page - handles authentication with username/email and password
 * Features:
 * - Form validation (client-side and server-side)
 * - Error handling and display
 * - Loading state with spinner
 * - Auto-redirect to dashboard on success
 * - Deep linking support (redirect to original path after login)
 * - Focus management and accessibility
 */

import { ref, computed, watch, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useI18n } from 'vue-i18n';
import AuthFormLayout from '@/components/auth/AuthFormLayout.vue';
import BaseInput from '@/components/auth/BaseInput.vue';
import BaseButton from '@/components/base/BaseButton.vue';
import InlineError from '@/components/base/InlineError.vue';
import type { LoginFormData } from '@/types/auth';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const { t } = useI18n();

// Form state
const formData = ref<LoginFormData>({
  username: '',
  password: '',
});

// UI state
const isSubmitting = ref(false);
const serverError = ref<string | null>(null);
const fieldErrors = ref<Partial<LoginFormData>>({});
const usernameInputRef = ref<InstanceType<typeof BaseInput>>();

/**
 * Computed property to check if form is valid
 * Both fields must be non-empty and trimmed
 */
const isFormValid = computed(() => {
  return formData.value.username.trim() !== '' && formData.value.password.trim() !== '';
});

/**
 * Clear server error when user starts editing
 */
function clearServerError() {
  serverError.value = null;
}

/**
 * Client-side form validation
 */
function validateForm(): boolean {
  const errors: Partial<LoginFormData> = {};
  let isValid = true;

  if (formData.value.username.trim() === '') {
    errors.username = t('login.errors.usernameRequired');
    isValid = false;
  }

  if (formData.value.password.trim() === '') {
    errors.password = t('login.errors.passwordRequired');
    isValid = false;
  }

  fieldErrors.value = errors;
  return isValid;
}

/**
 * Handle form submission
 */
async function handleSubmit() {
  serverError.value = null;
  fieldErrors.value = {};

  // Client-side validation
  if (!validateForm()) {
    serverError.value = t('login.errors.fillAllFields');
    return;
  }

  isSubmitting.value = true;

  try {
    // Attempt login
    await authStore.login({
      username: formData.value.username.trim(),
      password: formData.value.password.trim(),
    });

    // Success - redirect to target or dashboard
    const redirectPath = (route.query.redirect as string) || '/';
    await router.push(redirectPath);
  } catch {
    // Error is already mapped to user-friendly message in authStore
    serverError.value = authStore.error || t('errors.unexpectedError');

    // Focus back on username field for retry
    setTimeout(() => {
      if (usernameInputRef.value?.$el) {
        (usernameInputRef.value.$el as HTMLInputElement).focus();
      }
    }, 100);
  } finally {
    isSubmitting.value = false;
  }
}

/**
 * Navigate to register page
 */
function goToRegister() {
  router.push({ name: 'register' });
}

/**
 * Handle form submission on Enter key
 */
function handleKeyPress(event: KeyboardEvent) {
  if (event.key === 'Enter' && isFormValid.value && !isSubmitting.value) {
    handleSubmit();
  }
}

/**
 * Watch for changes in form fields to clear server errors
 */
watch(
  () => [formData.value.username, formData.value.password],
  () => {
    clearServerError();
  }
);

/**
 * Set focus on username field on mount
 */
onMounted(() => {
  if (usernameInputRef.value?.$el) {
    (usernameInputRef.value.$el as HTMLInputElement).focus();
  }
});
</script>

<template>
  <AuthFormLayout :title="$t('login.title')">
    <!-- Error Alert -->
    <InlineError v-if="serverError" :message="serverError" />

    <!-- Login Form -->
    <form class="space-y-4 sm:space-y-5" @submit.prevent="handleSubmit" @keypress="handleKeyPress">
      <!-- Username Input -->
      <BaseInput
        ref="usernameInputRef"
        v-model="formData.username"
        :label="$t('login.username')"
        type="text"
        autocomplete="username"
        :error="fieldErrors.username"
        :disabled="isSubmitting"
        @blur="clearServerError"
      />

      <!-- Password Input -->
      <BaseInput
        v-model="formData.password"
        :label="$t('login.password')"
        type="password"
        autocomplete="current-password"
        :error="fieldErrors.password"
        :disabled="isSubmitting"
        @blur="clearServerError"
      />

      <!-- Submit Button -->
      <BaseButton
        type="submit"
        variant="primary"
        :loading="isSubmitting"
        :disabled="!isFormValid || isSubmitting"
        full-width
      >
        {{ $t('login.submit') }}
      </BaseButton>
    </form>

    <!-- Register Link -->
    <template #links>
      <p class="text-sm text-gray-600 dark:text-gray-400">
        {{ $t('login.hasAccount') }}
        <button
          type="button"
          class="font-semibold text-blue-600 dark:text-blue-400 hover:underline transition-colors"
          @click="goToRegister"
        >
          {{ $t('login.register') }}
        </button>
      </p>
    </template>
  </AuthFormLayout>
</template>

<style scoped>
/* Smooth transitions */
@media (prefers-reduced-motion: reduce) {
  form {
    transition: none !important;
  }
}
</style>
