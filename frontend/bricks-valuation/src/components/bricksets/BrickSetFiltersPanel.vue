<script setup lang="ts">
/**
 * BrickSetFiltersPanel Component
 * Reusable filters panel with all filtering controls
 * Uses v-model pattern (modelValue + @update:modelValue)
 */

import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import type { BrickSetFiltersState, OrderingOption, SelectOption } from '@/types/bricksets';
import { VALID_ORDERING_OPTIONS } from '@/types/bricksets';
import BaseInput from '@/components/auth/BaseInput.vue';
import BaseCustomSelect from '@/components/base/BaseCustomSelect.vue';

defineProps<{
  modelValue: BrickSetFiltersState;
  disabled?: boolean;
}>();

const emit = defineEmits<{
  'update:modelValue': [filters: Partial<BrickSetFiltersState>];
  reset: [];
}>();

const { t } = useI18n();

// Select options
const productionStatusOptions = computed<SelectOption[]>(() => [
  { value: '', label: t('bricksets.allStatuses') },
  { value: 'ACTIVE', label: t('bricksets.active') },
  { value: 'RETIRED', label: t('bricksets.retired') },
]);

const completenessOptions = computed<SelectOption[]>(() => [
  { value: '', label: t('bricksets.allCompletion') },
  { value: 'COMPLETE', label: t('bricksets.complete') },
  { value: 'INCOMPLETE', label: t('bricksets.incomplete') },
]);

const orderingOptions = computed<SelectOption[]>(() => [
  { value: '-created_at', label: t('bricksets.newest') },
  { value: 'created_at', label: t('bricksets.oldest') },
]);

function handleSearchInput(value: string) {
  emit('update:modelValue', { q: value });
}

function handleProductionStatusChange(value: string) {
  emit('update:modelValue', { production_status: value || null });
}

function handleCompletenessChange(value: string) {
  emit('update:modelValue', { completeness: value || null });
}

function handleAttributeChange(
  attribute: 'has_instructions' | 'has_box' | 'is_factory_sealed',
  checked: boolean
) {
  emit('update:modelValue', { [attribute]: checked || null });
}

function handleOrderingChange(value: string) {
  const ordering = isOrderingOption(value) ? value : '-created_at';
  emit('update:modelValue', { ordering });
}

function handleReset() {
  emit('reset');
}

function isOrderingOption(value: string): value is OrderingOption {
  return VALID_ORDERING_OPTIONS.includes(value as OrderingOption);
}

function onHasInstructionsChange(event: Event) {
  handleAttributeChange('has_instructions', (event.target as HTMLInputElement).checked);
}

function onHasBoxChange(event: Event) {
  handleAttributeChange('has_box', (event.target as HTMLInputElement).checked);
}

function onIsFactorySealedChange(event: Event) {
  handleAttributeChange('is_factory_sealed', (event.target as HTMLInputElement).checked);
}
</script>

<template>
  <div
    data-testid="filters-panel"
    class="sticky top-4 bg-gray-800 rounded-lg border border-gray-700 p-4 space-y-4"
  >
    <!-- Search Input -->
    <div data-testid="search-input">
      <BaseInput
        :model-value="modelValue.q"
        :label="$t('bricksets.search')"
        type="search"
        placeholder="Numer zestawu..."
        :disabled="disabled"
        clearable
        @update:model-value="handleSearchInput"
      />
    </div>

    <!-- Production Status Select -->
    <div data-testid="production-status-filter">
      <BaseCustomSelect
        :model-value="modelValue.production_status || ''"
        :label="$t('bricksets.productionStatus')"
        :options="productionStatusOptions"
        :disabled="disabled"
        @update:model-value="handleProductionStatusChange"
      />
    </div>

    <!-- Completeness Select -->
    <div data-testid="completeness-filter">
      <BaseCustomSelect
        :model-value="modelValue.completeness || ''"
        :label="$t('bricksets.completeness')"
        :options="completenessOptions"
        :disabled="disabled"
        @update:model-value="handleCompletenessChange"
      />
    </div>

    <!-- Attribute Toggles -->
    <fieldset class="border-t border-gray-700 pt-4">
      <legend class="text-sm font-medium text-gray-300 mb-2">
        {{ $t('bricksets.attributes') }}
      </legend>
      <div class="space-y-2">
        <label class="flex items-center text-sm text-gray-300 cursor-pointer">
          <input
            type="checkbox"
            :checked="modelValue.has_instructions === true"
            :disabled="disabled"
            data-testid="has-instructions-checkbox"
            class="rounded bg-gray-900 border-gray-600 text-blue-600 focus:ring-blue-500 focus:ring-offset-gray-800 disabled:opacity-50"
            @change="onHasInstructionsChange"
          />
          <span class="ml-2">{{ $t('bricksets.hasInstructions') }}</span>
        </label>
        <label class="flex items-center text-sm text-gray-300 cursor-pointer">
          <input
            type="checkbox"
            :checked="modelValue.has_box === true"
            :disabled="disabled"
            data-testid="has-box-checkbox"
            class="rounded bg-gray-900 border-gray-600 text-blue-600 focus:ring-blue-500 focus:ring-offset-gray-800 disabled:opacity-50"
            @change="onHasBoxChange"
          />
          <span class="ml-2">{{ $t('bricksets.hasBox') }}</span>
        </label>
        <label class="flex items-center text-sm text-gray-300 cursor-pointer">
          <input
            type="checkbox"
            :checked="modelValue.is_factory_sealed === true"
            :disabled="disabled"
            class="rounded bg-gray-900 border-gray-600 text-blue-600 focus:ring-blue-500 focus:ring-offset-gray-800 disabled:opacity-50"
            @change="onIsFactorySealedChange"
          />
          <span class="ml-2">{{ $t('bricksets.sealed') }}</span>
        </label>
      </div>
    </fieldset>

    <!-- Ordering Select -->
    <div data-testid="ordering-select">
      <BaseCustomSelect
        :model-value="modelValue.ordering"
        :label="$t('bricksets.orderBy')"
        :options="orderingOptions"
        :disabled="disabled"
        @update:model-value="handleOrderingChange"
      />
    </div>

    <!-- Reset Button -->
    <button
      :disabled="disabled"
      data-testid="reset-filters-btn"
      class="w-full px-3 py-2 bg-gray-700 text-gray-200 rounded-md text-sm font-medium hover:bg-gray-600 disabled:opacity-50 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
      @click="handleReset"
    >
      {{ $t('common.reset') }}
    </button>
  </div>
</template>

<style scoped>
input:disabled,
button:disabled {
  cursor: not-allowed;
}
</style>
