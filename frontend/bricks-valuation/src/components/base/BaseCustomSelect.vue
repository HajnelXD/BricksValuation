<script setup lang="ts">
/**
 * BaseCustomSelect Component
 * Custom dropdown/select field component with animated chevron and full styling control
 *
 * Features:
 * - Custom dropdown with animated chevron (rotates 180° on open)
 * - Chevron positioned 4px from right edge
 * - Keyboard navigation (Arrow keys, Enter, Escape, Tab)
 * - Click outside to close
 * - Error state styling (red border + background)
 * - Disabled state with reduced opacity
 * - Full accessibility with ARIA attributes
 * - Search/filter support (optional)
 * - Dark mode support
 */

import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import type { SelectOption } from '@/types/bricksets';

const props = defineProps<{
  modelValue: string;
  label: string;
  options: SelectOption[];
  error?: string;
  placeholder?: string;
  disabled?: boolean;
  required?: boolean;
  searchable?: boolean;
}>();

const emit = defineEmits<{
  'update:modelValue': [value: string];
  blur: [];
  focus: [];
}>();

const isOpen = ref(false);
const searchQuery = ref('');
const dropdownRef = ref<HTMLDivElement | null>(null);
const buttonRef = ref<HTMLButtonElement | null>(null);
const focusedIndex = ref(-1);

const selectedOption = computed(() => {
  return props.options.find((opt) => opt.value === props.modelValue);
});

const displayText = computed(() => {
  return selectedOption.value?.label || props.placeholder || 'Select...';
});

const filteredOptions = computed(() => {
  if (!props.searchable || !searchQuery.value) {
    return props.options;
  }
  const query = searchQuery.value.toLowerCase();
  return props.options.filter((opt) => opt.label.toLowerCase().includes(query));
});

function toggleDropdown() {
  if (props.disabled) return;

  isOpen.value = !isOpen.value;

  if (isOpen.value) {
    emit('focus');
    searchQuery.value = '';
    focusedIndex.value = -1;
  } else {
    emit('blur');
  }
}

function selectOption(option: SelectOption) {
  if (option.disabled) return;

  emit('update:modelValue', option.value);
  isOpen.value = false;
  emit('blur');
  buttonRef.value?.focus();
}

function handleClickOutside(event: MouseEvent) {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
    isOpen.value = false;
    emit('blur');
  }
}

function handleKeydown(event: KeyboardEvent) {
  if (props.disabled) return;

  switch (event.key) {
    case 'Enter':
    case ' ':
      event.preventDefault();
      if (!isOpen.value) {
        isOpen.value = true;
        emit('focus');
      } else if (focusedIndex.value >= 0) {
        selectOption(filteredOptions.value[focusedIndex.value]);
      }
      break;
    case 'Escape':
      event.preventDefault();
      isOpen.value = false;
      emit('blur');
      buttonRef.value?.focus();
      break;
    case 'ArrowDown':
      event.preventDefault();
      if (!isOpen.value) {
        isOpen.value = true;
        emit('focus');
      } else {
        focusedIndex.value = Math.min(focusedIndex.value + 1, filteredOptions.value.length - 1);
      }
      break;
    case 'ArrowUp':
      event.preventDefault();
      if (isOpen.value) {
        focusedIndex.value = Math.max(focusedIndex.value - 1, 0);
      }
      break;
    case 'Tab':
      if (isOpen.value) {
        isOpen.value = false;
        emit('blur');
      }
      break;
  }
}

onMounted(() => {
  document.addEventListener('mousedown', handleClickOutside);
});

onBeforeUnmount(() => {
  document.removeEventListener('mousedown', handleClickOutside);
});
</script>

<template>
  <div ref="dropdownRef" class="space-y-2">
    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
      {{ label }}
      <span v-if="required" class="text-red-500 ml-1">*</span>
    </label>

    <div class="relative">
      <button
        ref="buttonRef"
        type="button"
        :disabled="disabled"
        :aria-invalid="!!error"
        :aria-describedby="error ? `error-${label}` : undefined"
        :aria-expanded="isOpen"
        :aria-haspopup="true"
        :class="[
          'w-full px-4 py-2.5 border rounded-lg shadow-sm transition-all duration-200',
          'focus:outline-none focus:ring-2 focus:ring-offset-0 focus:border-transparent',
          'text-sm sm:text-base text-left',
          'bg-white dark:bg-gray-800 dark:text-white',
          'flex items-center justify-between',
          error
            ? 'border-red-500 bg-red-50 dark:bg-red-900/20 dark:border-red-400 focus:ring-red-500'
            : 'border-gray-300 dark:border-gray-600 focus:ring-blue-500 focus:border-blue-500',
          disabled
            ? 'opacity-60 cursor-not-allowed'
            : 'hover:border-gray-400 dark:hover:border-gray-500 cursor-pointer',
          !selectedOption && placeholder ? 'text-gray-400 dark:text-gray-500' : '',
        ]"
        @click="toggleDropdown"
        @keydown="handleKeydown"
      >
        <span class="block truncate pr-2">{{ displayText }}</span>

        <!-- Animated Chevron Icon (4px from right edge) -->
        <svg
          :class="[
            'w-5 h-5 transition-transform duration-200 flex-shrink-0',
            'text-gray-400 dark:text-gray-500',
            isOpen ? 'rotate-180' : 'rotate-0',
          ]"
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
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </button>

      <!-- Dropdown Menu -->
      <Transition
        enter-active-class="transition ease-out duration-100"
        enter-from-class="transform opacity-0 scale-95"
        enter-to-class="transform opacity-100 scale-100"
        leave-active-class="transition ease-in duration-75"
        leave-from-class="transform opacity-100 scale-100"
        leave-to-class="transform opacity-0 scale-95"
      >
        <div
          v-show="isOpen"
          class="absolute z-50 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg max-h-60 overflow-auto"
        >
          <!-- Search Input (optional) -->
          <div v-if="searchable" class="p-2 border-b border-gray-200 dark:border-gray-700">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search..."
              class="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 dark:text-white"
              @click.stop
            />
          </div>

          <!-- Options List -->
          <ul role="listbox" class="py-1">
            <li
              v-for="(option, index) in filteredOptions"
              :key="option.value"
              role="option"
              :aria-selected="option.value === modelValue"
              :class="[
                'px-4 py-2.5 cursor-pointer transition-colors duration-150',
                'text-sm sm:text-base',
                option.value === modelValue
                  ? 'bg-blue-100 dark:bg-blue-900/50 text-blue-900 dark:text-blue-100 font-medium'
                  : 'text-gray-900 dark:text-gray-100',
                option.disabled
                  ? 'opacity-50 cursor-not-allowed'
                  : 'hover:bg-gray-100 dark:hover:bg-gray-700',
                index === focusedIndex ? 'bg-gray-50 dark:bg-gray-700' : '',
              ]"
              @click="selectOption(option)"
              @mouseenter="focusedIndex = index"
            >
              <div class="flex items-center justify-between">
                <span>{{ option.label }}</span>
                <svg
                  v-if="option.value === modelValue"
                  class="w-5 h-5 text-blue-600 dark:text-blue-400"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fill-rule="evenodd"
                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                    clip-rule="evenodd"
                  />
                </svg>
              </div>
            </li>

            <!-- Empty State -->
            <li
              v-if="filteredOptions.length === 0"
              class="px-4 py-2.5 text-sm text-gray-500 dark:text-gray-400 text-center"
            >
              No options found
            </li>
          </ul>
        </div>
      </Transition>
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
button:disabled {
  background-color: #f3f4f6;
}

.dark button:disabled {
  background-color: #1f2937;
}

/* Custom scrollbar for dropdown */
.overflow-auto::-webkit-scrollbar {
  width: 8px;
}

.overflow-auto::-webkit-scrollbar-track {
  background: transparent;
}

.overflow-auto::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 4px;
}

.dark .overflow-auto::-webkit-scrollbar-thumb {
  background: #4b5563;
}

.overflow-auto::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}

.dark .overflow-auto::-webkit-scrollbar-thumb:hover {
  background: #6b7280;
}

@media (prefers-reduced-motion: reduce) {
  button,
  svg,
  div,
  ul,
  li {
    transition: none !important;
    animation: none !important;
  }
}
</style>
