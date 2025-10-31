<script setup lang="ts">
/**
 * BaseInput Component
 * Universal form input field with label, error display, and accessibility features
 * Features:
 * - Focus states with ring indicator
 * - Error state styling (red border + background)
 * - Disabled state with reduced opacity
 * - Clear button (X icon) when input has value
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
  clearable?: boolean;
}>();

const emit = defineEmits<{
  'update:modelValue': [value: string];
  blur: [];
  focus: [];
}>();

function clearInput() {
  emit('update:modelValue', '');
}
</script>

<template>
  <div class="space-y-2">
    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
      {{ label }}
    </label>
    <div class="relative">
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
          clearable && modelValue ? 'pr-10' : '',
        ]"
        @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
        @blur="$emit('blur')"
        @focus="$emit('focus')"
      />

      <!-- Clear Button (X icon) -->
      <button
        v-if="clearable && modelValue && !disabled"
        type="button"
        class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors duration-200"
        aria-label="Clear input"
        @click="clearInput"
      >
        <svg
          class="w-5 h-5"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M6 18L18 6M6 6l12 12"
          />
        </svg>
      </button>
    </div>
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

/* Hide native clear button in search inputs (webkit browsers) */
input[type='search']::-webkit-search-cancel-button {
  -webkit-appearance: none;
  appearance: none;
}

/* Hide native clear button in search inputs (IE/Edge) */
input[type='search']::-ms-clear {
  display: none;
}

@media (prefers-reduced-motion: reduce) {
  input,
  div {
    transition: none !important;
    animation: none !important;
  }
}
</style>
