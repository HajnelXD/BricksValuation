<script setup lang="ts">
/**
 * RuleLockBadge Component
 * Displays a warning badge when BrickSet cannot be edited/deleted due to business rules
 * Shows specific reason based on the rule violation
 *
 * Features:
 * - Warning variant with yellow/amber styling
 * - Accessibility with alert role and aria-live
 * - Type-based messaging (edit, delete, both)
 * - Optional reason display
 */

import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import type { RuleLockType } from '@/types/bricksets';

interface Props {
  type: RuleLockType;
  reason?: string;
}

const props = defineProps<Props>();
const { t } = useI18n();

/**
 * Compute message based on lock type
 */
const message = computed(() => {
  if (props.type === 'edit') {
    return t('errors.edit_forbidden');
  } else if (props.type === 'delete') {
    return t('errors.delete_forbidden');
  } else {
    return t('errors.edit_delete_forbidden');
  }
});
</script>

<template>
  <div
    role="alert"
    aria-live="polite"
    class="flex items-start gap-3 p-4 rounded-lg bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 animate-in fade-in duration-200"
  >
    <!-- Warning Icon -->
    <svg
      xmlns="http://www.w3.org/2000/svg"
      class="flex-shrink-0 w-5 h-5 text-amber-600 dark:text-amber-500"
      viewBox="0 0 20 20"
      fill="currentColor"
      aria-hidden="true"
    >
      <path
        fill-rule="evenodd"
        d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
        clip-rule="evenodd"
      />
    </svg>

    <!-- Message Content -->
    <div class="flex-1">
      <p class="text-sm font-medium text-amber-800 dark:text-amber-300 leading-tight mb-1">
        {{ message }}
      </p>
      <p v-if="reason" class="text-xs text-amber-700 dark:text-amber-400 leading-snug">
        {{ reason }}
      </p>
    </div>
  </div>
</template>

<style scoped>
@media (prefers-reduced-motion: reduce) {
  div {
    animation: none !important;
  }
}
</style>
