<template>
  <div>
    <!-- Results count -->
    <div class="mb-6 text-sm text-gray-600 dark:text-gray-400">{{ valuations.length }} wycen</div>

    <!-- Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <OwnValuationCard
        v-for="valuation in valuations"
        :key="valuation.id"
        :valuation="valuation"
        @navigate-to-brickset="emit('navigate-to-brickset', $event)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { OwnValuationViewModel } from '@/types/bricksets';
import OwnValuationCard from './OwnValuationCard.vue';

interface Props {
  valuations: OwnValuationViewModel[];
}

defineProps<Props>();

defineEmits<{
  'navigate-to-brickset': [bricksetId: number];
}>();
</script>

<style scoped></style>
