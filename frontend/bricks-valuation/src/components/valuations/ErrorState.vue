<template>
  <div class="text-center py-16">
    <div class="text-6xl mb-4">⚠️</div>
    <h3 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">Coś poszło nie tak</h3>
    <p class="text-gray-600 dark:text-gray-400 mb-8">
      {{ error }}
    </p>
    <button
      :disabled="isLoading"
      class="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed dark:bg-blue-700 dark:hover:bg-blue-600"
      @click="emit('retry')"
    >
      <span v-if="!isLoading">{{ $t('common.retry') }}</span>
      <span v-else>Ładowanie...</span>
    </button>
  </div>
</template>

<script setup lang="ts">
interface Props {
  error: string;
  isLoading: boolean;
}

defineProps<Props>();

const emit = defineEmits<{
  retry: [];
}>();
</script>

<style scoped></style>
