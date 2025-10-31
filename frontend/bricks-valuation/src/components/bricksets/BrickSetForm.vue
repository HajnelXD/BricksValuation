<script setup lang="ts">
/**
 * BrickSetForm Component
 * Main form component for creating and editing BrickSets
 *
 * Features:
 * - Supports both create and edit modes
 * - Organized form sections (Identity, Status, Attributes, Estimate)
 * - Integration with useBrickSetForm composable
 * - Field validation with error display
 * - Form submission handling with success/error callbacks
 * - Keyboard support (Enter to submit, Escape to cancel)
 * - Dark mode and responsive layout
 */

import { useI18n } from 'vue-i18n';
import { watch } from 'vue';
import { useBrickSetForm } from '@/composables/useBrickSetForm';
import type {
  SelectOption,
  CreateBrickSetResponse,
  FormMode,
  BrickSetFormData,
} from '@/types/bricksets';
import BaseInput from '@/components/auth/BaseInput.vue';
import BaseCustomSelect from '@/components/base/BaseCustomSelect.vue';
import BaseCheckbox from '@/components/base/BaseCheckbox.vue';
import ValidationErrorList from '@/components/base/ValidationErrorList.vue';

interface Props {
  isLoading?: boolean;
  mode?: FormMode;
  initialData?: BrickSetFormData;
  readonlyFields?: string[];
}

const props = withDefaults(defineProps<Props>(), {
  isLoading: false,
  mode: 'create',
  initialData: undefined,
  readonlyFields: () => [],
});

const emit = defineEmits<{
  'on-submit': [response: CreateBrickSetResponse];
  'on-error': [error: unknown];
  'on-cancel': [];
  'update:isDirty': [isDirty: boolean];
  'update:formData': [formData: BrickSetFormData];
}>();

const { t } = useI18n();
const form = useBrickSetForm();

// Initialize form with initial data in edit mode
if (props.mode === 'edit' && props.initialData) {
  Object.assign(form.formData, props.initialData);
}

// Watch isDirty and emit changes to parent
watch(
  () => form.isDirty,
  (newValue: boolean) => {
    emit('update:isDirty', newValue);
  }
);

// Watch formData and emit changes to parent
watch(
  () => form.formData,
  (newValue: BrickSetFormData) => {
    emit('update:formData', newValue);
  },
  { deep: true }
);

// Build select options from i18n
const productionStatusOptions: SelectOption[] = [
  { value: 'ACTIVE', label: t('bricksets.active') },
  { value: 'RETIRED', label: t('bricksets.retired') },
];

const completenessOptions: SelectOption[] = [
  { value: 'COMPLETE', label: t('bricksets.complete') },
  { value: 'INCOMPLETE', label: t('bricksets.incomplete') },
];

/**
 * Check if a field is readonly
 */
function isFieldReadonly(fieldName: string): boolean {
  return props.readonlyFields.includes(fieldName);
}

/**
 * Handle form submission
 */
async function handleSubmit(): Promise<void> {
  try {
    const response = await form.submitForm();
    emit('on-submit', response);
  } catch (error) {
    // Emit error event to parent for handling
    emit('on-error', error);
    // Errors are already set in form.fieldErrors by submitForm
    // Component will re-render and show validation errors
    console.error('Form submission error:', error);
  }
}

/**
 * Handle form cancel/back
 */
function handleCancel(): void {
  emit('on-cancel');
}

/**
 * Handle field value changes and validation
 */
function handleFieldChange(
  fieldName: keyof BrickSetFormData,
  value: string | boolean | null
): void {
  form.setFieldValue(fieldName, value);
  form.validateField(fieldName);
}

/**
 * Handle Enter key for form submission
 */
function handleKeyDown(event: KeyboardEvent): void {
  if (event.key === 'Enter' && event.ctrlKey) {
    event.preventDefault();
    handleSubmit();
  } else if (event.key === 'Escape') {
    event.preventDefault();
    handleCancel();
  }
}

/**
 * Expose form state to parent component
 * Used for accessing formData in edit mode
 */
defineExpose({
  form,
});
</script>

<template>
  <form
    class="max-w-2xl mx-auto px-4 py-8 sm:px-6 lg:px-8"
    @submit.prevent="handleSubmit"
    @keydown="handleKeyDown"
  >
    <!-- Form Header -->
    <div class="mb-8">
      <h1 class="text-2xl sm:text-3xl font-bold text-white">
        {{ t('bricksets.create.title') }}
      </h1>
    </div>

    <!-- General Server Errors -->
    <ValidationErrorList
      v-if="form.fieldErrors.general"
      :errors="form.fieldErrors.general || []"
      type="error"
      is-dismissible
    />

    <!-- Form Content -->
    <div class="mt-8 space-y-8">
      <!-- Section 1: BrickSet Identity -->
      <fieldset class="space-y-4">
        <legend class="text-lg font-semibold text-white mb-4">
          {{ t('bricksets.create.section.identity') }}
        </legend>

        <BaseInput
          :model-value="form.formData.number"
          :label="t('bricksets.create.fields.number.label')"
          :placeholder="t('bricksets.create.fields.number.placeholder')"
          :error="form.fieldErrors.number"
          type="number"
          :disabled="form.isSubmitting.value || isFieldReadonly('number')"
          @update:model-value="(val: string) => handleFieldChange('number', val)"
          @blur="() => form.validateField('number')"
        />
      </fieldset>

      <!-- Section 2: Production Status and Completeness -->
      <fieldset class="space-y-4">
        <legend class="text-lg font-semibold text-white mb-4">
          {{ t('bricksets.create.section.status') }}
        </legend>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <BaseCustomSelect
            :model-value="form.formData.productionStatus"
            :label="t('bricksets.create.fields.productionStatus.label')"
            :options="productionStatusOptions"
            :error="form.fieldErrors.productionStatus"
            :disabled="form.isSubmitting.value || isFieldReadonly('productionStatus')"
            required
            @update:model-value="(val: string) => handleFieldChange('productionStatus', val)"
            @blur="() => form.validateField('productionStatus')"
          />

          <BaseCustomSelect
            :model-value="form.formData.completeness"
            :label="t('bricksets.create.fields.completeness.label')"
            :options="completenessOptions"
            :error="form.fieldErrors.completeness"
            :disabled="form.isSubmitting.value || isFieldReadonly('completeness')"
            required
            @update:model-value="(val: string) => handleFieldChange('completeness', val)"
            @blur="() => form.validateField('completeness')"
          />
        </div>
      </fieldset>

      <!-- Section 3: Set Attributes -->
      <fieldset class="space-y-4">
        <legend class="text-lg font-semibold text-white mb-4">
          {{ t('bricksets.create.section.attributes') }}
        </legend>

        <div class="space-y-3">
          <BaseCheckbox
            :model-value="form.formData.hasInstructions"
            :label="t('bricksets.create.fields.hasInstructions.label')"
            :description="t('bricksets.create.fields.hasInstructions.description')"
            :disabled="form.isSubmitting.value || isFieldReadonly('hasInstructions')"
            @update:model-value="(val: boolean) => handleFieldChange('hasInstructions', val)"
          />

          <BaseCheckbox
            :model-value="form.formData.hasBox"
            :label="t('bricksets.create.fields.hasBox.label')"
            :description="t('bricksets.create.fields.hasBox.description')"
            :disabled="form.isSubmitting.value || isFieldReadonly('hasBox')"
            @update:model-value="(val: boolean) => handleFieldChange('hasBox', val)"
          />

          <BaseCheckbox
            :model-value="form.formData.isFactorySealed"
            :label="t('bricksets.create.fields.isFactorySealed.label')"
            :description="t('bricksets.create.fields.isFactorySealed.description')"
            :disabled="form.isSubmitting.value || isFieldReadonly('isFactorySealed')"
            @update:model-value="(val: boolean) => handleFieldChange('isFactorySealed', val)"
          />
        </div>
      </fieldset>

      <!-- Section 4: Owner's Initial Estimate (Optional) -->
      <fieldset class="space-y-4">
        <legend class="text-lg font-semibold text-white mb-4">
          {{ t('bricksets.create.section.estimate') }}
        </legend>

        <BaseInput
          :model-value="form.formData.ownerInitialEstimate || ''"
          :label="t('bricksets.create.fields.ownerInitialEstimate.label')"
          :placeholder="t('bricksets.create.fields.ownerInitialEstimate.placeholder')"
          :error="form.fieldErrors.ownerInitialEstimate"
          type="number"
          :disabled="form.isSubmitting.value || isFieldReadonly('ownerInitialEstimate')"
          @update:model-value="
            (val: string) => handleFieldChange('ownerInitialEstimate', val || null)
          "
          @blur="() => form.validateField('ownerInitialEstimate')"
        />
        <p class="text-xs text-gray-400 mt-2">
          {{ t('bricksets.create.fields.ownerInitialEstimate.hint') }}
        </p>
      </fieldset>

      <!-- Form Hint -->
      <div class="bg-blue-900/30 border border-blue-700 rounded-lg p-4">
        <p class="text-sm text-blue-200">
          {{ t('bricksets.create.formHint') }}
        </p>
      </div>
    </div>

    <!-- Bottom Form Actions (only in create mode) -->
    <div
      v-if="mode === 'create'"
      class="mt-8 flex flex-col-reverse sm:flex-row justify-between gap-4"
    >
      <button
        type="button"
        :disabled="form.isSubmitting.value"
        class="px-4 py-2.5 rounded-lg font-semibold transition-all duration-200 text-white bg-gray-700 hover:bg-gray-600 disabled:opacity-60 disabled:cursor-not-allowed"
        @click="handleCancel"
      >
        {{ t('common.cancel') }}
      </button>
      <button
        type="submit"
        :disabled="form.hasErrors.value || form.isSubmitting.value"
        class="px-4 py-2.5 rounded-lg font-semibold transition-all duration-200 text-white bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2"
      >
        <svg
          v-if="form.isSubmitting.value"
          class="w-4 h-4 animate-spin flex-shrink-0"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
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
        {{ t('bricksets.create.submit') }}
      </button>
    </div>

    <!-- Keyboard Shortcuts Hint (only in create mode) -->
    <div v-if="mode === 'create'" class="mt-6 text-center text-xs text-gray-500 dark:text-gray-400">
      <p>{{ t('common.keyboardShortcuts') }}</p>
    </div>
  </form>
</template>

<style scoped>
fieldset {
  border: none;
}

legend {
  padding: 0;
}

@media (prefers-reduced-motion: reduce) {
  * {
    transition: none !important;
    animation: none !important;
  }
}
</style>
