<script setup lang="ts">
/**
 * BaseTextarea Component
 * Textarea field for comments with character counter and validation
 *
 * Features:
 * - Character counter (X/MAX)
 * - Max length enforcement via maxlength attribute
 * - Color indicator when near limit (red when >1900/2000)
 * - Full accessibility with aria-invalid, aria-describedby
 * - Error state styling (red border + background)
 * - Disabled state with reduced opacity
 * - Responsive sizing with configurable rows
 */

defineProps<{
  modelValue: string;
  label: string;
  error?: string;
  placeholder?: string;
  disabled?: boolean;
  maxlength?: number;
  rows?: number;
  required?: boolean;
}>();

defineEmits<{
  'update:modelValue': [value: string];
  blur: [];
  focus: [];
}>();

const DEFAULT_MAX_LENGTH = 2000;
const WARNING_THRESHOLD = 1900;

function getCounterColor(current: number, max: number) {
  if (current > max) return 'text-red-600 dark:text-red-400';
  if (current >= WARNING_THRESHOLD) return 'text-orange-600 dark:text-orange-400';
  return 'text-gray-500 dark:text-gray-400';
}
</script>

<template>
  <div class="space-y-2">
    <div class="flex items-center justify-between">
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
        {{ label }}
        <span v-if="required" class="text-red-500 ml-1" aria-label="required">*</span>
      </label>
      <span
        class="text-xs transition-colors duration-200"
        :class="getCounterColor(modelValue.length, maxlength || DEFAULT_MAX_LENGTH)"
        aria-live="polite"
      >
        {{ modelValue.length }} / {{ maxlength || DEFAULT_MAX_LENGTH }}
      </span>
    </div>

    <textarea
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      :maxlength="maxlength || DEFAULT_MAX_LENGTH"
      :rows="rows || 4"
      :aria-invalid="!!error"
      :aria-describedby="error ? `error-${label}` : undefined"
      :aria-required="required"
      :class="[
        'w-full px-4 py-2.5 border rounded-lg shadow-sm placeholder-gray-400 transition-all duration-200',
        'focus:outline-none focus:ring-2 focus:ring-offset-0 focus:border-transparent resize-vertical',
        'text-sm sm:text-base leading-relaxed',
        error
          ? 'border-red-500 bg-red-50 dark:bg-red-900/20 dark:border-red-400 focus:ring-red-500'
          : 'border-gray-300 bg-white dark:bg-gray-800 dark:border-gray-600 dark:text-white focus:ring-blue-500 focus:border-blue-500',
        disabled
          ? 'opacity-60 cursor-not-allowed bg-gray-100 dark:bg-gray-700'
          : 'hover:border-gray-400 dark:hover:border-gray-500',
      ]"
      @input="$emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
      @blur="$emit('blur')"
      @focus="$emit('focus')"
    />

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
textarea:disabled {
  background-color: #f3f4f6;
}

/* Ensure consistent appearance across browsers */
textarea {
  font-family: inherit;
  line-height: 1.5;
}

@media (prefers-reduced-motion: reduce) {
  textarea,
  div {
    transition: none !important;
    animation: none !important;
  }
}
</style>
