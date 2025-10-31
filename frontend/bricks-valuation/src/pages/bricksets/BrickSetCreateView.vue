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

import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { useNotificationStore } from '@/stores/notification';
import type { CreateBrickSetResponse, DuplicateSetInfo } from '@/types/bricksets';
import BrickSetForm from '@/components/bricksets/BrickSetForm.vue';
import BrickSetDuplicateModal from '@/components/modals/BrickSetDuplicateModal.vue';
import { DuplicateError } from '@/composables/useBrickSetForm';

const router = useRouter();
const { t } = useI18n();
const notificationStore = useNotificationStore();

// Modal state
const isDuplicateModalOpen = ref(false);
const duplicateSetInfo = ref<DuplicateSetInfo | null>(null);

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
  // Check if it's a DuplicateError
  if (error instanceof DuplicateError) {
    // Extract duplicate info and show modal
    // The composable already stored the duplicate info
    if (error.duplicateInfo) {
      duplicateSetInfo.value = error.duplicateInfo;
      isDuplicateModalOpen.value = true;
    } else {
      // This should not happen, but fallback to notification
      notificationStore.error(t('bricksets.create.errors.duplicate'), 7000);
    }
  } else {
    const errorObj = error as { name?: string; message?: string };

    if (errorObj.name === 'ValidationError') {
      // Validation errors are already set in form.fieldErrors
      // Component will display them inline
    } else {
      // Other errors
      notificationStore.error(t('errors.networkError'), 5000);
    }
  }
}

/**
 * Close duplicate modal
 */
function closeDuplicateModal(): void {
  isDuplicateModalOpen.value = false;
}

/**
 * Handle navigation from duplicate modal
 */
function handleDuplicateNavigation(): void {
  // Modal will handle the navigation, we just close it
  isDuplicateModalOpen.value = false;
}

/**
 * Handle form cancel/back
 */
function handleFormCancel(): void {
  router.back();
}
</script>

<template>
  <div class="min-h-screen bg-gray-900">
    <!-- Page Content -->
    <BrickSetForm
      @on-submit="handleFormSubmit"
      @on-error="handleFormError"
      @on-cancel="handleFormCancel"
    />

    <!-- Duplicate Detection Modal -->
    <BrickSetDuplicateModal
      v-if="isDuplicateModalOpen && duplicateSetInfo"
      :is-open="isDuplicateModalOpen"
      :duplicate-set-info="duplicateSetInfo"
      @close="closeDuplicateModal"
      @navigate="handleDuplicateNavigation"
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
