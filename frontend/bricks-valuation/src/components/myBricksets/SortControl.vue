<script setup lang="ts">
/**
 * SortControl Component
 * Dropdown/select for sorting My BrickSets list
 * Options: by creation date, number of valuations, or number of likes
 */

import type { SortOrderingValue, SortOption } from '@/types/bricksets';

interface Props {
  modelValue: SortOrderingValue;
  options: SortOption[];
}

defineProps<Props>();

const emit = defineEmits<{
  'update:modelValue': [value: SortOrderingValue];
}>();

function handleChange(event: Event) {
  const target = event.target as HTMLSelectElement;
  emit('update:modelValue', target.value as SortOrderingValue);
}
</script>

<template>
  <div class="flex items-center gap-2">
    <label for="sort-select" class="text-sm font-medium text-gray-300">
      {{ $t('myBrickSets.sort.label') }}:
    </label>
    <select
      id="sort-select"
      :value="modelValue"
      class="px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      @change="handleChange"
    >
      <option v-for="option in options" :key="option.value" :value="option.value">
        {{ option.label }}
      </option>
    </select>
  </div>
</template>

<style scoped>
select {
  transition: all 0.2s ease-in-out;
}

select:hover:not(:disabled) {
  border-color: #4b5563;
}

select:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
