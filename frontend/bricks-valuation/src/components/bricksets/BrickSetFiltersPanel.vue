<script setup lang="ts">
/**
 * BrickSetFiltersPanel Component
 * Reusable filters panel with all filtering controls
 * Uses v-model pattern (modelValue + @update:modelValue)
 */

import type { BrickSetFiltersState, OrderingOption } from '@/types/bricksets';
import { VALID_ORDERING_OPTIONS } from '@/types/bricksets';

defineProps<{
  modelValue: BrickSetFiltersState;
  disabled?: boolean;
}>();

const emit = defineEmits<{
  'update:modelValue': [filters: Partial<BrickSetFiltersState>];
  reset: [];
}>();

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

function onSearchInput(event: Event) {
  handleSearchInput((event.target as HTMLInputElement).value);
}

function onProductionStatusChange(event: Event) {
  handleProductionStatusChange((event.target as HTMLSelectElement).value);
}

function onCompletenessChange(event: Event) {
  handleCompletenessChange((event.target as HTMLSelectElement).value);
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

function onOrderingChange(event: Event) {
  handleOrderingChange((event.target as HTMLSelectElement).value);
}
</script>

<template>
  <div
    data-testid="filters-panel"
    class="sticky top-4 bg-white rounded-lg border border-gray-200 p-4 space-y-4"
  >
    <!-- Search Input -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-2">
        {{ $t('bricksets.search') }}
      </label>
      <input
        type="search"
        :value="modelValue.q"
        :disabled="disabled"
        data-testid="search-input"
        placeholder="Numer zestawu..."
        class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm disabled:opacity-50"
        @input="onSearchInput"
      />
    </div>

    <!-- Production Status Select -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-2">
        {{ $t('bricksets.productionStatus') }}
      </label>
      <select
        :value="modelValue.production_status || ''"
        :disabled="disabled"
        data-testid="production-status-filter"
        class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm disabled:opacity-50"
        @change="onProductionStatusChange"
      >
        <option value="">{{ $t('bricksets.allStatuses') }}</option>
        <option value="ACTIVE">{{ $t('bricksets.active') }}</option>
        <option value="RETIRED">{{ $t('bricksets.retired') }}</option>
      </select>
    </div>

    <!-- Completeness Select -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-2">
        {{ $t('bricksets.completeness') }}
      </label>
      <select
        :value="modelValue.completeness || ''"
        :disabled="disabled"
        data-testid="completeness-filter"
        class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm disabled:opacity-50"
        @change="onCompletenessChange"
      >
        <option value="">{{ $t('bricksets.allCompletion') }}</option>
        <option value="COMPLETE">{{ $t('bricksets.complete') }}</option>
        <option value="INCOMPLETE">{{ $t('bricksets.incomplete') }}</option>
      </select>
    </div>

    <!-- Attribute Toggles -->
    <fieldset class="border-t pt-4">
      <legend class="text-sm font-medium text-gray-700 mb-2">
        {{ $t('bricksets.attributes') }}
      </legend>
      <div class="space-y-2">
        <label class="flex items-center text-sm">
          <input
            type="checkbox"
            :checked="modelValue.has_instructions === true"
            :disabled="disabled"
            data-testid="has-instructions-checkbox"
            class="rounded disabled:opacity-50"
            @change="onHasInstructionsChange"
          />
          <span class="ml-2">{{ $t('bricksets.hasInstructions') }}</span>
        </label>
        <label class="flex items-center text-sm">
          <input
            type="checkbox"
            :checked="modelValue.has_box === true"
            :disabled="disabled"
            data-testid="has-box-checkbox"
            class="rounded disabled:opacity-50"
            @change="onHasBoxChange"
          />
          <span class="ml-2">{{ $t('bricksets.hasBox') }}</span>
        </label>
        <label class="flex items-center text-sm">
          <input
            type="checkbox"
            :checked="modelValue.is_factory_sealed === true"
            :disabled="disabled"
            class="rounded disabled:opacity-50"
            @change="onIsFactorySealedChange"
          />
          <span class="ml-2">{{ $t('bricksets.sealed') }}</span>
        </label>
      </div>
    </fieldset>

    <!-- Ordering Select -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-2">
        {{ $t('bricksets.orderBy') }}
      </label>
      <select
        :value="modelValue.ordering"
        :disabled="disabled"
        data-testid="ordering-select"
        class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm disabled:opacity-50"
        @change="onOrderingChange"
      >
        <option value="-created_at">{{ $t('bricksets.newest') }}</option>
        <option value="created_at">{{ $t('bricksets.oldest') }}</option>
        <option value="-popular">{{ $t('bricksets.popular') }}</option>
        <option value="-valuations">{{ $t('bricksets.mostValuations') }}</option>
      </select>
    </div>

    <!-- Reset Button -->
    <button
      :disabled="disabled"
      data-testid="reset-filters-btn"
      class="w-full px-3 py-2 bg-gray-200 text-gray-700 rounded-md text-sm font-medium hover:bg-gray-300 disabled:opacity-50 transition-colors"
      @click="handleReset"
    >
      {{ $t('common.reset') }}
    </button>
  </div>
</template>

<style scoped>
input:disabled,
select:disabled,
button:disabled {
  cursor: not-allowed;
}
</style>
