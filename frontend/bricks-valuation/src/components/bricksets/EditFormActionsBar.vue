<script setup lang="ts">
/**
 * EditFormActionsBar Component
 * Action bar for BrickSet edit form with Save, Cancel, and Delete buttons
 *
 * Features:
 * - Three-button layout: Save (primary), Cancel (secondary), Delete (danger)
 * - Loading states for save and delete operations
 * - Disabled states based on form validity and permissions
 * - Conditional display of Delete button
 * - Responsive layout
 * - Accessibility with proper aria labels
 */

import BaseButton from '@/components/base/BaseButton.vue';
import type { FormActionsConfig } from '@/types/bricksets';

interface Props {
  config: FormActionsConfig;
  showDelete?: boolean;
}

withDefaults(defineProps<Props>(), {
  showDelete: false,
});

defineEmits<{
  save: [];
  cancel: [];
  delete: [];
}>();
</script>

<template>
  <div
    class="flex items-center justify-between gap-4 pt-6 border-t border-gray-200 dark:border-gray-700"
  >
    <!-- Left side: Delete button (if allowed) -->
    <div>
      <BaseButton
        v-if="showDelete && config.canDelete"
        variant="danger"
        :disabled="config.isDeleting || config.isSaving"
        :loading="config.isDeleting"
        aria-label="Usuń zestaw"
        @click="$emit('delete')"
      >
        {{ config.isDeleting ? 'Usuwanie...' : 'Usuń' }}
      </BaseButton>
    </div>

    <!-- Right side: Save and Cancel buttons -->
    <div class="flex items-center gap-3">
      <BaseButton
        variant="secondary"
        :disabled="config.isSaving || config.isDeleting"
        aria-label="Anuluj edycję"
        @click="$emit('cancel')"
      >
        Anuluj
      </BaseButton>

      <BaseButton
        type="submit"
        variant="primary"
        :disabled="!config.canSave || config.isSaving || config.isDeleting"
        :loading="config.isSaving"
        aria-label="Zapisz zmiany"
        @click="$emit('save')"
      >
        {{ config.isSaving ? 'Zapisywanie...' : 'Zapisz zmiany' }}
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
