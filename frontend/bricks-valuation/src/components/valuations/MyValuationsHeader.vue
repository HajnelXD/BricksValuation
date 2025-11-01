<template>
  <div class="mb-8">
    <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
      {{ $t('nav.myValuations') }}
    </h1>
    <p class="text-gray-600 dark:text-gray-400 mb-4">
      <span v-if="totalValuations === 1"> Masz 1 wycenę </span>
      <span v-else> Masz {{ totalValuations }} wycen </span>
      <span v-if="totalLikes > 0" class="ml-2"> • {{ totalLikes }} lajków </span>
    </p>
    <router-link
      to="/bricksets"
      class="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors dark:bg-blue-700 dark:hover:bg-blue-600"
    >
      Dodaj wycenę
    </router-link>
  </div>
</template>

<script setup lang="ts">
interface Props {
  totalValuations?: number;
  totalLikes?: number;
}

withDefaults(defineProps<Props>(), {
  totalValuations: 0,
  totalLikes: 0,
});
</script>

<style scoped></style>
