<script setup lang="ts">
/**
 * BaseCheckbox Component
 * Checkbox input component for boolean fields with label and optional description
 *
 * Features:
 * - Standard HTML checkbox element
 * - Clickable label for better UX
 * - Optional description/hint text
 * - Dark mode support
 * - Accessibility with proper labeling
 */

defineProps<{
  modelValue: boolean;
  label: string;
  description?: string;
  disabled?: boolean;
  hint?: string;
}>();

defineEmits<{
  'update:modelValue': [value: boolean];
  blur: [];
  focus: [];
}>();
</script>

<template>
  <div class="space-y-2">
    <div class="flex items-center gap-3">
      <input
        :checked="modelValue"
        type="checkbox"
        :disabled="disabled"
        class="w-4 h-4 text-blue-500 bg-gray-100 border-gray-300 rounded focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 cursor-pointer"
        :class="disabled ? 'opacity-60 cursor-not-allowed' : 'hover:border-gray-400'"
        @change="$emit('update:modelValue', ($event.target as HTMLInputElement).checked)"
        @blur="$emit('blur')"
        @focus="$emit('focus')"
      />
      <div class="flex-1">
        <label class="text-sm font-medium text-gray-700 dark:text-gray-300 cursor-pointer">
          {{ label }}
        </label>
        <p v-if="description" class="text-xs text-gray-500 dark:text-gray-400 mt-1">
          {{ description }}
        </p>
      </div>
    </div>
    <p v-if="hint" class="text-xs text-gray-500 dark:text-gray-400 ml-7">
      {{ hint }}
    </p>
  </div>
</template>

<style scoped>
input:disabled {
  opacity: 0.6;
}

@media (prefers-reduced-motion: reduce) {
  input {
    transition: none !important;
    animation: none !important;
  }
}
</style>
