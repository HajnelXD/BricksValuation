<script setup lang="ts">
/**
 * EmptyState Component
 * Displayed when user has no bricksets
 * Shows encouraging message and action button to add first set
 */

import { useRouter } from 'vue-router';

const router = useRouter();

function handleAddBrickset() {
  router.push('/app/bricksets/new');
}
</script>

<template>
  <div class="flex flex-col items-center justify-center py-12 px-4">
    <!-- Icon -->
    <div class="text-6xl mb-4">📦</div>

    <!-- Title -->
    <h3 class="text-xl font-semibold text-white mb-2">
      {{ $t('myBrickSets.empty.title') }}
    </h3>

    <!-- Description -->
    <p class="text-gray-400 text-center mb-6 max-w-md">
      {{ $t('myBrickSets.empty.description') }}
    </p>

    <!-- Action Button -->
    <button
      class="px-6 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
      @click="handleAddBrickset"
    >
      {{ $t('myBrickSets.empty.action') }}
    </button>
  </div>
</template>

<style scoped>
button {
  transition: background-color 0.2s ease-in-out;
}

button:focus-visible {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}
</style>
