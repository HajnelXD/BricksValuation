<script setup lang="ts">
/**
 * FormActionsBar Component
 * Reusable header component for forms displaying title, action buttons, and navigation controls
 *
 * Features:
 * - Title/heading with semantic HTML
 * - Back/Cancel button on the left
 * - Submit button on the right with loading state
 * - Optional breadcrumbs or navigation context
 * - Responsive layout
 */

import BaseButton from '@/components/base/BaseButton.vue';

interface Props {
  title: string;
  submitText?: string;
  cancelText?: string;
  isSubmitting?: boolean;
  showBackButton?: boolean;
  submitDisabled?: boolean;
}

withDefaults(defineProps<Props>(), {
  submitText: 'Dodaj zestaw',
  cancelText: 'Anuluj',
  showBackButton: true,
  isSubmitting: false,
  submitDisabled: false,
});

defineEmits<{
  back: [];
  submit: [];
}>();
</script>

<template>
  <div
    class="flex items-center justify-between gap-4 pb-6 border-b border-gray-200 dark:border-gray-700"
  >
    <h1 class="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">
      {{ title }}
    </h1>

    <div class="flex items-center gap-3">
      <BaseButton
        v-if="showBackButton !== false"
        variant="secondary"
        :disabled="isSubmitting"
        @click="$emit('back')"
      >
        {{ cancelText }}
      </BaseButton>

      <BaseButton
        type="submit"
        variant="primary"
        :disabled="submitDisabled || isSubmitting"
        :is-loading="isSubmitting"
        @click="$emit('submit')"
      >
        {{ submitText }}
      </BaseButton>
    </div>
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
