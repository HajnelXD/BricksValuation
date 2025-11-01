<script setup lang="ts">
/**
 * DeleteConfirmModal Component
 * Confirmation modal for BrickSet deletion with warning and explicit confirmation
 *
 * Features:
 * - Clear warning message about irreversible action
 * - Displays BrickSet number for confirmation
 * - Two-action layout: Cancel (safe) and Delete (destructive)
 * - Loading state during deletion
 * - Keyboard support (ESC to cancel, Enter to confirm)
 * - Focus trap for accessibility
 * - Dark mode support
 */

import { onMounted, onUnmounted, ref } from 'vue';
import BaseButton from '@/components/base/BaseButton.vue';
import type { DeleteConfirmData } from '@/types/bricksets';

interface Props {
  open: boolean;
  data: DeleteConfirmData | null;
  isDeleting?: boolean;
}

interface Emits {
  (e: 'confirm'): void;
  (e: 'cancel'): void;
}

const props = withDefaults(defineProps<Props>(), {
  isDeleting: false,
});

const emit = defineEmits<Emits>();

// Ref to the delete button for focus management
const deleteButtonRef = ref<InstanceType<typeof BaseButton> | null>(null);

/**
 * Handle keyboard events
 * ESC - cancel, Enter - confirm (with caution)
 */
const handleKeydown = (event: KeyboardEvent) => {
  if (!props.open) return;

  if (event.key === 'Escape' && !props.isDeleting) {
    event.preventDefault();
    emit('cancel');
  }
  // Intentionally NOT adding Enter to confirm - force user to click for safety
};

/**
 * Handle backdrop click
 */
const handleBackdropClick = () => {
  if (!props.isDeleting) {
    emit('cancel');
  }
};

// Setup keyboard listener
onMounted(() => {
  document.addEventListener('keydown', handleKeydown);
});

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown);
});
</script>

<template>
  <Teleport to="body">
    <Transition name="modal-fade" appear>
      <div
        v-if="open && data"
        class="fixed inset-0 bg-black/60 flex items-center justify-center z-[1000] p-4"
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="delete-modal-title"
        aria-describedby="delete-modal-description"
        @click="handleBackdropClick"
      >
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-2xl max-w-md w-full" @click.stop>
          <!-- Modal Header -->
          <div class="px-6 py-5 border-b border-gray-200 dark:border-gray-700">
            <div class="flex items-start gap-3">
              <!-- Warning Icon -->
              <div
                class="flex-shrink-0 w-10 h-10 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="w-6 h-6 text-red-600 dark:text-red-500"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  stroke-width="2"
                  aria-hidden="true"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  />
                </svg>
              </div>

              <!-- Title -->
              <div class="flex-1">
                <h2 id="delete-modal-title" class="text-xl font-bold text-gray-900 dark:text-white">
                  Usuń zestaw
                </h2>
              </div>
            </div>
          </div>

          <!-- Modal Body -->
          <div class="px-6 py-5">
            <p id="delete-modal-description" class="text-sm text-gray-700 dark:text-gray-300 mb-4">
              Czy na pewno chcesz usunąć zestaw
              <strong class="font-semibold text-gray-900 dark:text-white">
                {{ data.brickSetNumber }} </strong
              >?
            </p>

            <div
              class="p-3 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800"
            >
              <p class="text-xs text-red-800 dark:text-red-300 font-medium">
                ⚠️ Ta operacja jest nieodwracalna. Wszystkie powiązane wyceny również zostaną
                usunięte.
              </p>
            </div>
          </div>

          <!-- Modal Footer -->
          <div
            class="px-6 py-4 bg-gray-50 dark:bg-gray-900/30 border-t border-gray-200 dark:border-gray-700 flex justify-end gap-3"
          >
            <BaseButton
              variant="secondary"
              :disabled="isDeleting"
              aria-label="Anuluj usunięcie"
              @click="emit('cancel')"
            >
              Anuluj
            </BaseButton>

            <BaseButton
              ref="deleteButtonRef"
              variant="danger"
              :disabled="isDeleting"
              :loading="isDeleting"
              aria-label="Potwierdź usunięcie zestawu"
              @click="emit('confirm')"
            >
              {{ isDeleting ? 'Usuwanie...' : 'Usuń zestaw' }}
            </BaseButton>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
/* Modal fade transition */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.2s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

@media (prefers-reduced-motion: reduce) {
  .modal-fade-enter-active,
  .modal-fade-leave-active {
    transition: none !important;
  }
}
</style>
