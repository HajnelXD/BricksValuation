<script setup lang="ts">
/**
 * BaseInput Component
 * Universal form input field with label, error display, and accessibility features
 * Features:
 * - Focus states with ring indicator
 * - Error state styling (red border + background)
 * - Disabled state with reduced opacity
 * - Full accessibility with aria-invalid, aria-describedby
 * - Responsive sizing
 */

defineProps<{
  modelValue: string;
  label: string;
  type?: string;
  error?: string;
  placeholder?: string;
  disabled?: boolean;
  autocomplete?: string;
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
    </label>
    <input
      :value="modelValue"
      :type="type || 'text'"
      :placeholder="placeholder"
      :disabled="disabled"
      :autocomplete="autocomplete"
      :aria-invalid="!!error"
      :aria-describedby="error ? `error-${label}` : undefined"
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
      ]"
      @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
      @blur="$emit('blur')"
      @focus="$emit('focus')"
    />
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

@media (prefers-reduced-motion: reduce) {
  input,
  div {
    transition: none !important;
    animation: none !important;
  }
}
</style>
