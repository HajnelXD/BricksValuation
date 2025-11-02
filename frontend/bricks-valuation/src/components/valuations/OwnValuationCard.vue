<template>
  <div
    class="bg-white dark:bg-gray-800 rounded-lg shadow-md hover:shadow-lg transition-shadow p-6 cursor-pointer"
    @click="handleNavigate"
  >
    <!-- Header: Brickset reference -->
    <div class="mb-4 pb-4 border-b border-gray-200 dark:border-gray-700">
      <router-link
        :to="`/bricksets/${valuation.bricksetId}`"
        class="text-lg font-semibold text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300"
      >
        {{ valuation.bricksetNumber }}
      </router-link>
    </div>

    <!-- Middle: Valuation value -->
    <div class="mb-4 py-4">
      <p class="text-4xl font-bold text-gray-900 dark:text-white">
        {{ valuation.valueFormatted }}
      </p>
    </div>

    <!-- Footer: Stats and action -->
    <div
      class="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700"
    >
      <div class="flex gap-6 text-sm text-gray-600 dark:text-gray-400">
        <span>❤️ {{ valuation.likesCount }}</span>
        <span>{{ valuation.createdAtRelative }}</span>
      </div>
      <router-link
        :to="`/bricksets/${valuation.bricksetId}`"
        class="inline-flex items-center text-sm font-medium text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300"
      >
        Przejdź
        <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { OwnValuationViewModel } from '@/types/bricksets';

interface Props {
  valuation: OwnValuationViewModel;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  'navigate-to-brickset': [bricksetId: number];
}>();

function handleNavigate() {
  emit('navigate-to-brickset', props.valuation.bricksetId);
}
</script>

<style scoped></style>
