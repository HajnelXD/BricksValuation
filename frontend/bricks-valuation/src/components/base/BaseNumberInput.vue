<script setup lang="ts">
/**
 * BaseNumberInput Component
 * Number input field for valuation values with currency suffix and validation
 *
 * Features:
 * - Type="number" input for numeric values
 * - Currency suffix display (e.g., "PLN")
 * - Full accessibility with aria-invalid, aria-describedby
 * - Error state styling (red border + background)
 * - Disabled state with reduced opacity
 * - Responsive sizing
 */

defineProps<{
  modelValue: number | null;
  label: string;
  error?: string;
  placeholder?: string;
  disabled?: boolean;
  min?: number;
  max?: number;
  step?: string | number;
  currencyCode?: string; // e.g., "PLN"
  required?: boolean;
}>();

const emit = defineEmits<{
  'update:modelValue': [value: number | null];
  blur: [];
  focus: [];
}>();

function handleInput(event: Event) {
  const target = event.target as HTMLInputElement;
  const value = target.value;
  const numValue = value === '' ? null : parseFloat(value);
  emit('update:modelValue', numValue);
}
</script>

<template>
  <div class="space-y-2">
    <div class="flex items-center justify-between">
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
        {{ label }}
        <span v-if="required" class="text-red-500 ml-1" aria-label="required">*</span>
      </label>
    </div>

    <div class="relative">
      <input
        :value="modelValue !== null ? modelValue : ''"
        type="number"
        :placeholder="placeholder"
        :disabled="disabled"
        :min="min"
        :max="max"
        :step="step"
        :aria-invalid="!!error"
        :aria-describedby="error ? `error-${label}` : undefined"
        :aria-required="required"
        :class="[
          'w-full px-4 py-2.5 border rounded-lg shadow-sm placeholder-gray-400 transition-all duration-200',
          'focus:outline-none focus:ring-2 focus:ring-offset-0 focus:border-transparent',
          'text-sm sm:text-base',
          error
            ? 'border-red-500 bg-red-50 dark:bg-red-900/20 dark:border-red-400 focus:ring-red-500'
            : 'border-gray-300 bg-white dark:bg-gray-800 dark:border-gray-600 dark:text-white focus:ring-blue-500 focus:border-blue-500',
          disabled
            ? 'opacity-60 cursor-not-allowed bg-gray-100 dark:bg-gray-700'
            : 'hover:border-gray-400 dark:hover:border-gray-500',
          currencyCode ? 'pr-14' : '',
        ]"
        @input="handleInput"
        @blur="$emit('blur')"
        @focus="$emit('focus')"
      />

      <!-- Currency Suffix -->
      <span
        v-if="currencyCode"
        class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 dark:text-gray-400 font-medium pointer-events-none"
        aria-hidden="true"
      >
        {{ currencyCode }}
      </span>
    </div>

    <!-- Error Message -->
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
input:disabled {
  background-color: #f3f4f6;
}

/* Remove spinner arrows from number input */
input[type='number']::-webkit-inner-spin-button,
input[type='number']::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

input[type='number'] {
  -moz-appearance: textfield;
}

@media (prefers-reduced-motion: reduce) {
  input,
  div {
    transition: none !important;
    animation: none !important;
  }
}
</style>
