<script setup lang="ts">
/**
 * TopValuationSnippet Component
 * Displays the highest-liked valuation snippet in a highlighted box
 */

import type { TopValuationViewModel } from '@/types/bricksets';

defineProps<{
  valuation: TopValuationViewModel;
}>();
</script>

<template>
  <div class="bg-yellow-50 border border-yellow-200 rounded p-2 text-sm">
    <p class="font-semibold text-yellow-900">
      TOP: {{ valuation.valueFormatted }}
    </p>
    <p class="text-yellow-700">
      ❤️ {{ valuation.likesCount }}
    </p>
  </div>
</template>

<style scoped></style>
