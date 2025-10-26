<template>
  <div data-testid="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <div v-for="i in count" :key="i" class="animate-pulse">
      <div class="bg-gray-200 dark:bg-gray-700 rounded-lg p-4 h-64 space-y-3">
        <!-- Image skeleton -->
        <div class="bg-gray-300 dark:bg-gray-600 rounded w-full h-40"></div>

        <!-- Title skeleton -->
        <div class="h-4 bg-gray-300 dark:bg-gray-600 rounded w-3/4"></div>

        <!-- Description skeleton -->
        <div class="space-y-2">
          <div class="h-3 bg-gray-300 dark:bg-gray-600 rounded"></div>
          <div class="h-3 bg-gray-300 dark:bg-gray-600 rounded w-5/6"></div>
        </div>

        <!-- Footer info skeleton -->
        <div class="flex justify-between pt-2">
          <div class="h-4 bg-gray-300 dark:bg-gray-600 rounded w-1/4"></div>
          <div class="h-4 bg-gray-300 dark:bg-gray-600 rounded w-1/4"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  count?: number;
}>();
</script>

<style scoped>
@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>
