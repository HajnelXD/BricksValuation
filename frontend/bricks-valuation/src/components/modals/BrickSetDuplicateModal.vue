<script setup lang="ts">
/**
 * BrickSetDuplicateModal Component
 * Modal displayed when user attempts to create a duplicate BrickSet
 *
 * Features:
 * - Shows detailed information about the duplicate set
 * - Allows user to navigate to existing set or close modal
 * - Displays all critical fields that matched
 * - Supports dark mode and responsive layout
 * - Accessibility support with ARIA labels and keyboard navigation
 */

import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import type { DuplicateSetInfo } from '@/types/bricksets';

interface Props {
  isOpen: boolean;
  duplicateSetInfo: DuplicateSetInfo;
}

interface Emits {
  (e: 'close'): void;
  (e: 'navigate'): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();
const router = useRouter();
const { t } = useI18n();

const onClose = () => emit('close');

const onNavigateToExisting = async () => {
  if (props.duplicateSetInfo.setId && props.duplicateSetInfo.setId > 0) {
    // Navigate to specific set detail if ID is available
    await router.push({
      name: 'brickset-detail',
      params: { id: props.duplicateSetInfo.setId },
    });
  } else {
    // Navigate to list with search query
    await router.push({
      name: 'bricksets',
      query: { q: props.duplicateSetInfo.setNumber.toString() },
    });
  }
  emit('navigate');
  emit('close');
};

// Handle escape key to close modal
const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Escape') {
    onClose();
  }
};
</script>

<template>
  <Teleport to="#app">
    <div
      v-if="isOpen"
      class="fixed top-0 inset-0 bg-black/50 flex items-center justify-center z-[1000] p-4"
      role="dialog"
      aria-modal="true"
      :aria-labelledby="`modal-title-${duplicateSetInfo.setNumber}`"
      @click="onClose"
      @keydown="handleKeydown"
    >
      <div
        class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-[500px] w-full max-h-[90vh] overflow-y-auto"
        @click.stop
      >
        <!-- Modal Header -->
        <div
          class="flex justify-between items-center px-5 py-4 border-b border-gray-200 dark:border-gray-700"
        >
          <h2
            :id="`modal-title-${duplicateSetInfo.setNumber}`"
            class="text-xl sm:text-2xl font-semibold text-gray-900 dark:text-white"
          >
            {{ t('bricksets.duplicate.title') }}
          </h2>
          <button
            class="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500 dark:text-gray-400 text-2xl w-8 h-8 flex items-center justify-center transition-colors"
            :aria-label="t('common.close')"
            type="button"
            @click="onClose"
          >
            ✕
          </button>
        </div>

        <!-- Modal Body -->
        <div class="px-5 py-4 space-y-4">
          <p class="text-gray-700 dark:text-gray-300 leading-relaxed">
            {{ t('bricksets.duplicate.message') }}
          </p>

          <!-- Duplicate Set Info Card -->
          <div
            class="bg-gray-50 dark:bg-gray-700 border-l-4 border-amber-500 dark:border-amber-400 rounded p-4 space-y-3"
          >
            <h3 class="text-base font-semibold text-gray-900 dark:text-white mb-3">
              {{ t('bricksets.duplicate.existingSet') }}
            </h3>

            <!-- Set Number -->
            <div class="flex justify-between items-center gap-3">
              <span class="text-sm font-medium text-gray-600 dark:text-gray-400">
                {{ t('bricksets.create.fields.number.label') }}:
              </span>
              <span class="text-sm font-semibold text-gray-900 dark:text-white text-right">
                {{ duplicateSetInfo.setNumber }}
              </span>
            </div>

            <!-- Production Status -->
            <div class="flex justify-between items-center gap-3">
              <span class="text-sm font-medium text-gray-600 dark:text-gray-400">
                {{ t('bricksets.create.fields.productionStatus.label') }}:
              </span>
              <span class="text-sm font-semibold text-gray-900 dark:text-white text-right">
                {{ t(`bricksets.${duplicateSetInfo.productionStatus.toLowerCase()}`) }}
              </span>
            </div>

            <!-- Completeness -->
            <div class="flex justify-between items-center gap-3">
              <span class="text-sm font-medium text-gray-600 dark:text-gray-400">
                {{ t('bricksets.create.fields.completeness.label') }}:
              </span>
              <span class="text-sm font-semibold text-gray-900 dark:text-white text-right">
                {{ t(`bricksets.${duplicateSetInfo.completeness.toLowerCase()}`) }}
              </span>
            </div>

            <!-- Attributes Badges -->
            <div class="flex flex-wrap gap-2 pt-2">
              <span
                v-if="duplicateSetInfo.hasInstructions"
                class="attribute-badge inline-block bg-gray-300 dark:bg-gray-600 text-gray-800 dark:text-gray-100 px-2 py-1 rounded text-xs font-medium"
              >
                {{ t('bricksets.create.fields.hasInstructions.label') }}
              </span>
              <span
                v-if="duplicateSetInfo.hasBox"
                class="attribute-badge inline-block bg-gray-300 dark:bg-gray-600 text-gray-800 dark:text-gray-100 px-2 py-1 rounded text-xs font-medium"
              >
                {{ t('bricksets.create.fields.hasBox.label') }}
              </span>
              <span
                v-if="duplicateSetInfo.isFactorySealed"
                class="attribute-badge inline-block bg-gray-300 dark:bg-gray-600 text-gray-800 dark:text-gray-100 px-2 py-1 rounded text-xs font-medium"
              >
                {{ t('bricksets.create.fields.isFactorySealed.label') }}
              </span>
            </div>
          </div>

          <!-- Help Text -->
          <p class="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
            {{ t('bricksets.duplicate.helpText') }}
          </p>
        </div>

        <!-- Modal Footer -->
        <div
          class="flex justify-end gap-3 px-5 py-4 border-t border-gray-200 dark:border-gray-700 flex-col-reverse sm:flex-row"
        >
          <button
            class="px-4 py-2 rounded-md border border-transparent font-medium text-sm transition-colors bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
            type="button"
            @click="onClose"
          >
            {{ t('common.close') }}
          </button>
          <button
            class="px-4 py-2 rounded-md border border-transparent font-medium text-sm transition-colors bg-blue-600 hover:bg-blue-700 dark:bg-blue-700 dark:hover:bg-blue-600 text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            type="button"
            @click="onNavigateToExisting"
          >
            {{ t('bricksets.duplicate.viewExisting') }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
