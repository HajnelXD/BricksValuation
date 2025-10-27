<script setup lang="ts">
/**
 * BrickSetCreateView
 * Page component for creating a new BrickSet
 * Manages form submission, error handling, and navigation
 *
 * Features:
 * - Form submission with success/error handling
 * - Duplicate detection (409 Conflict) with modal
 * - Authorization check (401 Unauthorized) with redirect
 * - Success notification with navigation
 * - Error handling with user-friendly messages
 */

import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { useNotificationStore } from '@/stores/notification';
import type { CreateBrickSetResponse } from '@/types/bricksets';
import BrickSetForm from '@/components/bricksets/BrickSetForm.vue';

const router = useRouter();
const { t } = useI18n();
const notificationStore = useNotificationStore();

/**
 * Handle successful form submission
 */
async function handleFormSubmit(response: CreateBrickSetResponse): Promise<void> {
  // Show success notification
  notificationStore.success(t('bricksets.create.success', { number: response.number }), 5000);

  // Navigate to the public bricksets landing page
  await router.push({
    name: 'public-bricksets',
  });
}

/**
 * Handle form submission errors
 */
function handleFormError(error: unknown): void {
  const errorObj = error as { name?: string; message?: string };

  if (errorObj.name === 'DuplicateError') {
    // Handle duplicate set - show error message on the form
    notificationStore.error(t('bricksets.create.errors.duplicate'), 7000);
  } else if (errorObj.name === 'ValidationError') {
    // Validation errors are already set in form.fieldErrors
    // Component will display them inline
    console.log('Validation errors displayed');
  } else {
    // Other errors
    notificationStore.error(t('errors.networkError'), 5000);
  }
}

/**
 * Handle form cancel/back
 */
function handleFormCancel(): void {
  router.back();
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Page Content -->
    <BrickSetForm
      @on-submit="handleFormSubmit"
      @on-error="handleFormError"
      @on-cancel="handleFormCancel"
    />
  </div>
</template>

<style scoped>
@media (prefers-reduced-motion: reduce) {
  * {
    transition: none !important;
    animation: none !important;
  }
}
</style>
