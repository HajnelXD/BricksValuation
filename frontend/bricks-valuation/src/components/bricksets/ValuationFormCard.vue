<script setup lang="ts">
/**
 * ValuationFormCard Component
 * Inline form for adding valuations to a BrickSet
 *
 * Features:
 * - Valuation value field only (no comments)
 * - Real-time validation with field-level error display
 * - API integration via useValuationForm composable
 * - General error handling with InlineError component
 * - Loading state with button spinner
 * - Form reset after successful submission
 * - Accessibility features (aria labels, focus management)
 * - Dark mode support
 *
 * Props:
 * - bricksetId: ID of the brickset to add valuation for
 *
 * Emits:
 * - valuation-created: Fired with CreateValuationResponse after successful submission
 */

import { useI18n } from 'vue-i18n';
import { useValuationForm } from '@/composables/useValuationForm';
import type { CreateValuationResponse } from '@/types/bricksets';
import BaseNumberInput from '@/components/base/BaseNumberInput.vue';
import BaseButton from '@/components/base/BaseButton.vue';
import InlineError from '@/components/base/InlineError.vue';

interface Props {
  bricksetId: number;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  'valuation-created': [response: CreateValuationResponse];
  cancel: [];
}>();

const { t } = useI18n();
const form = useValuationForm(props.bricksetId);

/**
 * Handle value field input and mark as touched
 */
function handleValueInput(value: number | null): void {
  form.formData.value.value = value;
  // Clear general error when user starts typing
  if (form.errors.value.general) {
    delete form.errors.value.general;
  }
}

/**
 * Handle value field blur - trigger validation and mark touched
 */
function handleValueBlur(): void {
  form.markFieldTouched('value');
  form.validateField('value');
}

/**
 * Handle form submission
 */
async function handleSubmit(): Promise<void> {
  try {
    const response = await form.handleSubmit();

    if (response) {
      // Emit success event with response data
      emit('valuation-created', response);
      // Reset form for potential next use
      form.resetForm();
    }
  } catch (error) {
    // Error is already handled and set in form.errors
    // Component will automatically re-render and display errors
    console.error('Valuation submission error:', error);
  }
}
</script>

<template>
  <div class="mt-8 p-6 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm">
    <!-- Card Header -->
    <div class="mb-6">
      <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
        {{ t('valuation.form.title') }}
      </h2>
      <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
        {{ t('valuation.form.description') }}
      </p>
    </div>

    <!-- Form -->
    <form class="space-y-5" @submit.prevent="handleSubmit">
      <!-- General API Errors -->
      <InlineError
        v-if="form.errors.value.general"
        :message="form.errors.value.general"
        dismissible
        @dismiss="
          () => {
            delete form.errors.value.general;
          }
        "
      />

      <!-- Value Field -->
      <BaseNumberInput
        :model-value="form.formData.value.value"
        :label="t('valuation.form.value.label')"
        :placeholder="t('valuation.form.value.placeholder')"
        :error="form.touchedFields.value.has('value') ? form.errors.value.value : undefined"
        :disabled="form.isSubmitting.value"
        :min="1"
        :max="999999"
        currency-code="PLN"
        required
        @update:model-value="handleValueInput"
        @blur="handleValueBlur"
      />

      <!-- Form Actions -->
      <div class="flex gap-3 pt-4">
        <BaseButton
          type="submit"
          variant="primary"
          :disabled="!form.canSubmit.value"
          :loading="form.isSubmitting.value"
          full-width
        >
          {{
            form.isSubmitting.value
              ? t('valuation.form.submitting')
              : t('valuation.form.submit')
          }}
        </BaseButton>
      </div>

      <!-- Validation Help Text -->
      <div class="text-xs text-gray-500 dark:text-gray-400 space-y-1 mt-4 pt-2 border-t border-gray-200 dark:border-gray-700">
        <p>{{ t('valuation.form.help.valueRange') }}</p>
      </div>
    </form>
  </div>
</template>

<style scoped>
@media (prefers-reduced-motion: reduce) {
  div {
    animation: none !important;
    transition: none !important;
  }
}
</style>
