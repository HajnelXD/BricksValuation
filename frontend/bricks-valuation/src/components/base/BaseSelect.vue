<script setup lang="ts">
/**
 * BaseSelect Component
 * Dropdown/select field component with label, error display, and accessibility features
 *
 * Features:
 * - Standard HTML select element
 * - Error state styling (red border + background)
 * - Disabled state with reduced opacity
 * - Full accessibility with aria-invalid, aria-describedby
 * - Support for option groups (via slots)
 */

import type { SelectOption } from '@/types/bricksets';

defineProps<{
  modelValue: string;
  label: string;
  options: SelectOption[];
  error?: string;
  placeholder?: string;
  disabled?: boolean;
  required?: boolean;
}>();

defineEmits<{
  'update:modelValue': [value: string];
  blur: [];
  focus: [];
}>();
</script>

<template>
  <div class="space-y-2">
    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
      {{ label }}
      <span v-if="required" class="text-red-500 ml-1">*</span>
    </label>
    <select
      :value="modelValue"
      :disabled="disabled"
      :aria-invalid="!!error"
      :aria-describedby="error ? `error-${label}` : undefined"
      :class="[
        'w-full px-4 py-2.5 border rounded-lg shadow-sm transition-all duration-200',
        'focus:outline-none focus:ring-2 focus:ring-offset-0 focus:border-transparent',
        'text-sm sm:text-base',
        'bg-white dark:bg-gray-800 dark:text-white',
        error
          ? 'border-red-500 bg-red-50 dark:bg-red-900/20 dark:border-red-400 focus:ring-red-500'
          : 'border-gray-300 dark:border-gray-600 focus:ring-blue-500 focus:border-blue-500',
        disabled
          ? 'opacity-60 cursor-not-allowed'
          : 'hover:border-gray-400 dark:hover:border-gray-500',
      ]"
      @change="$emit('update:modelValue', ($event.target as HTMLSelectElement).value)"
      @blur="$emit('blur')"
      @focus="$emit('focus')"
    >
      <option v-if="placeholder" value="">{{ placeholder }}</option>
      <option
        v-for="option in options"
        :key="option.value"
        :value="option.value"
        :disabled="option.disabled"
      >
        {{ option.label }}
      </option>
    </select>
    <div
      v-if="error"
      :id="`error-${label}`"
      class="flex items-start gap-2 mt-1.5 text-sm text-red-600 dark:text-red-400 animate-in fade-in duration-200"
      role="alert"
    >
      <span class="flex-shrink-0 mt-0.5">⚠️</span>
      <span class="leading-tight">{{ error }}</span>
    </div>
  </div>
</template>

<style scoped>
select:disabled {
  background-color: #f3f4f6;
}

@media (prefers-reduced-motion: reduce) {
  select,
  div {
    transition: none !important;
    animation: none !important;
  }
}
</style>
