<script setup lang="ts">
/**
 * EditableIndicator Component
 * Shows a pencil icon indicating if brickset is editable
 * - If editable: active icon, clickable, tooltip with action text
 * - If not editable: grayed icon, non-clickable, tooltip with lock reason
 */

interface Props {
  editable: boolean;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  'edit-click': [];
}>();

function handleClick() {
  if (props.editable) {
    emit('edit-click');
  }
}

function handleKeydown(event: KeyboardEvent) {
  if (props.editable && (event.key === 'Enter' || event.key === ' ')) {
    event.preventDefault();
    emit('edit-click');
  }
}
</script>

<template>
  <div class="relative">
    <!-- Tooltip Trigger -->
    <button
      :disabled="!editable"
      :title="
        editable
          ? $t('myBrickSets.editable.tooltipEditable')
          : $t('myBrickSets.editable.tooltipNotEditable')
      "
      :class="[
        'p-2 rounded-lg transition-colors',
        editable
          ? 'text-blue-400 hover:bg-blue-900/30 cursor-pointer'
          : 'text-gray-500 cursor-not-allowed opacity-50',
      ]"
      @click.stop="handleClick"
      @keydown="handleKeydown"
    >
      <span class="text-lg">✏️</span>
    </button>

    <!-- Tooltip on Hover -->
    <div
      v-if="!editable"
      class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 text-gray-300 text-xs rounded-lg whitespace-nowrap opacity-0 pointer-events-none transition-opacity z-10"
      :class="{ 'opacity-100': !editable }"
    >
      {{ $t('myBrickSets.editable.tooltipNotEditable') }}
      <div
        class="absolute top-full left-1/2 -translate-x-1/2 -translate-y-1 border-4 border-transparent border-t-gray-900"
      ></div>
    </div>
  </div>
</template>

<style scoped>
button {
  transition: all 0.2s ease-in-out;
}

button:not(:disabled):focus-visible {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

button:disabled {
  cursor: not-allowed;
}
</style>
