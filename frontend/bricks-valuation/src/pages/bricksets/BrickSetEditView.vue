<script setup lang="ts">
/**
 * BrickSetEditView
 * View for editing existing BrickSets
 * Implements business rules for edit/delete permissions
 *
 * Features:
 * - Fetches BrickSet with edit/delete flags
 * - Validates edit/delete permissions
 * - Shows RuleLockBadge when operations are forbidden
 * - Integrates BrickSetForm in edit mode
 * - Handles partial updates (only changed fields)
 * - Delete confirmation modal
 * - Success/error notifications
 * - Navigation after operations
 */

import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useBrickSetEdit } from '@/composables/useBrickSetEdit';
import { useAuthStore } from '@/stores/auth';
import { useNotificationStore } from '@/stores/notification';
import { brickSetToFormData, generateUpdateDTO, cloneFormData } from '@/utils/formHelpers';
import BrickSetForm from '@/components/bricksets/BrickSetForm.vue';
import RuleLockBadge from '@/components/bricksets/RuleLockBadge.vue';
import EditFormActionsBar from '@/components/bricksets/EditFormActionsBar.vue';
import DeleteConfirmModal from '@/components/modals/DeleteConfirmModal.vue';
import ErrorState from '@/components/bricksets/ErrorState.vue';
import LoadingSkeletons from '@/components/bricksets/LoadingSkeletons.vue';
import type {
  BrickSetFormData,
  FormActionsConfig,
  DeleteConfirmData,
  RuleLockType,
} from '@/types/bricksets';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const notificationStore = useNotificationStore();

const { brickSet, isLoading, error, fetchBrickSet, updateBrickSet, deleteBrickSet } =
  useBrickSetEdit();

// Local state
const isSaving = ref(false);
const isDeleting = ref(false);
const showDeleteModal = ref(false);
const deleteConfirmData = ref<DeleteConfirmData | null>(null);
const formComponentRef = ref<InstanceType<typeof BrickSetForm> | null>(null);
const originalFormData = ref<BrickSetFormData | null>(null);

// Computed properties
const brickSetId = computed(() => {
  const id = route.params.id;
  return typeof id === 'string' ? Number.parseInt(id, 10) : null;
});

const canEdit = computed(() => {
  return brickSet.value?.editable ?? false;
});

const canDelete = computed(() => {
  return brickSet.value?.deletable ?? false;
});

const ruleLockType = computed((): RuleLockType | null => {
  if (!canEdit.value && !canDelete.value) return 'both';
  if (!canEdit.value) return 'edit';
  if (!canDelete.value) return 'delete';
  return null;
});

const formActionsConfig = computed((): FormActionsConfig => {
  return {
    canSave: canEdit.value && (formComponentRef.value?.form.isDirty ?? false),
    canDelete: canDelete.value,
    isSaving: isSaving.value,
    isDeleting: isDeleting.value,
  };
});

/**
 * Initialize form data from BrickSet
 */
function initializeForm() {
  if (brickSet.value) {
    const data = brickSetToFormData(brickSet.value);
    originalFormData.value = cloneFormData(data);
    // Form component will initialize its own formData
  }
}

/**
 * Handle form submission (save changes)
 */
async function handleSave() {
  if (!brickSetId.value || !formComponentRef.value || !originalFormData.value || !canEdit.value) {
    return;
  }

  isSaving.value = true;

  try {
    // Get current form data from the form component
    const currentFormData = formComponentRef.value.form.formData;

    const updateDTO = generateUpdateDTO(currentFormData, originalFormData.value);

    // Check if there are any changes
    if (Object.keys(updateDTO).length === 0) {
      notificationStore.addNotification({
        type: 'info',
        message: 'Brak zmian do zapisania',
      });
      isSaving.value = false;
      return;
    }

    await updateBrickSet(brickSetId.value, updateDTO);

    notificationStore.addNotification({
      type: 'success',
      message: 'Zestaw został zaktualizowany pomyślnie',
    });

    // Navigate back to detail view
    await router.push({
      name: 'brickset-detail',
      params: { id: brickSetId.value },
    });
  } catch (err: unknown) {
    if (err && typeof err === 'object' && 'type' in err && err.type === 'VALIDATION_ERROR') {
      notificationStore.addNotification({
        type: 'error',
        message: 'Popraw błędy walidacji w formularzu',
      });
    } else if (err instanceof Error) {
      const errorMessages: Record<string, string> = {
        BRICKSET_EDIT_FORBIDDEN: 'Nie możesz edytować tego zestawu',
        NOT_AUTHENTICATED: 'Sesja wygasła. Zaloguj się ponownie',
        BRICKSET_NOT_FOUND: 'Nie znaleziono zestawu',
        UPDATE_FAILED: 'Błąd podczas aktualizacji zestawu',
      };

      notificationStore.addNotification({
        type: 'error',
        message: errorMessages[err.message] || 'Wystąpił błąd podczas zapisywania',
      });
    }
  } finally {
    isSaving.value = false;
  }
}

/**
 * Handle cancel action
 */
function handleCancel() {
  router.push({
    name: 'brickset-detail',
    params: { id: brickSetId.value! },
  });
}

/**
 * Handle delete button click
 */
function handleDeleteClick() {
  if (!brickSet.value || !canDelete.value) return;

  deleteConfirmData.value = {
    brickSetNumber: brickSet.value.number.toString(),
    brickSetId: brickSet.value.id,
  };
  showDeleteModal.value = true;
}

/**
 * Handle delete confirmation
 */
async function handleDeleteConfirm() {
  if (!brickSetId.value) return;

  isDeleting.value = true;

  try {
    await deleteBrickSet(brickSetId.value);

    notificationStore.addNotification({
      type: 'success',
      message: 'Zestaw został usunięty pomyślnie',
    });

    showDeleteModal.value = false;

    // Navigate to list view
    await router.push({ name: 'public-bricksets' });
  } catch (err: unknown) {
    if (err instanceof Error) {
      const errorMessages: Record<string, string> = {
        BRICKSET_DELETE_FORBIDDEN: 'Nie możesz usunąć tego zestawu',
        NOT_AUTHENTICATED: 'Sesja wygasła. Zaloguj się ponownie',
        BRICKSET_NOT_FOUND: 'Nie znaleziono zestawu',
        DELETE_FAILED: 'Błąd podczas usuwania zestawu',
      };

      notificationStore.addNotification({
        type: 'error',
        message: errorMessages[err.message] || 'Wystąpił błąd podczas usuwania',
      });
    }
  } finally {
    isDeleting.value = false;
  }
}

/**
 * Handle delete cancel
 */
function handleDeleteCancel() {
  showDeleteModal.value = false;
}

/**
 * Handle retry on error
 */
function handleRetry() {
  if (brickSetId.value) {
    fetchBrickSet(brickSetId.value);
  }
}

/**
 * Load BrickSet on mount
 */
onMounted(async () => {
  if (!authStore.isAuthenticated) {
    notificationStore.addNotification({
      type: 'error',
      message: 'Musisz być zalogowany, aby edytować zestaw',
    });
    await router.push({ name: 'login' });
    return;
  }

  if (!brickSetId.value) {
    notificationStore.addNotification({
      type: 'error',
      message: 'Nieprawidłowy identyfikator zestawu',
    });
    await router.push({ name: 'bricksets' });
    return;
  }

  try {
    await fetchBrickSet(brickSetId.value);
    initializeForm();
  } catch (err: unknown) {
    // Error is already set in composable
    console.error('Failed to fetch BrickSet:', err);
  }
});
</script>

<template>
  <div class="min-h-screen bg-gray-900 py-8">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Loading State -->
      <LoadingSkeletons v-if="isLoading" />

      <!-- Error State -->
      <ErrorState v-else-if="error" :message="error" @retry="handleRetry" />

      <!-- Edit Form -->
      <div v-else-if="brickSet">
        <!-- Page Header -->
        <div class="mb-6">
          <h1 class="text-3xl font-bold text-white">Edytuj zestaw {{ brickSet.number }}</h1>
          <p class="text-sm text-gray-400 mt-2">ID właściciela: {{ brickSet.owner_id }}</p>
        </div>

        <!-- Rule Lock Badge (if applicable) -->
        <RuleLockBadge v-if="ruleLockType" :type="ruleLockType" class="mb-6" />

        <!-- Form -->
        <div class="bg-gray-800 rounded-lg shadow-xl p-6">
          <BrickSetForm
            ref="formComponentRef"
            mode="edit"
            :initial-data="brickSet ? brickSetToFormData(brickSet) : undefined"
            :readonly-fields="[
              'number',
              'productionStatus',
              'completeness',
              'hasInstructions',
              'isFactorySealed',
            ]"
            @on-submit="handleSave"
            @on-cancel="handleCancel"
          />

          <!-- Actions Bar -->
          <EditFormActionsBar
            :config="formActionsConfig"
            :show-delete="canDelete"
            @save="handleSave"
            @cancel="handleCancel"
            @delete="handleDeleteClick"
          />
        </div>
      </div>

      <!-- Delete Confirmation Modal -->
      <DeleteConfirmModal
        :open="showDeleteModal"
        :data="deleteConfirmData"
        :is-deleting="isDeleting"
        @confirm="handleDeleteConfirm"
        @cancel="handleDeleteCancel"
      />
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
