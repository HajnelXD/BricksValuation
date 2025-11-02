<template>
  <div
    class="flex items-center justify-between py-6 mt-8 border-t border-gray-200 dark:border-gray-700"
  >
    <div class="text-sm text-gray-600 dark:text-gray-400">
      Strona {{ currentPage }} z {{ totalPages }}
      <span class="ml-2">({{ totalCount }} wycen)</span>
    </div>

    <div class="flex gap-3">
      <button
        :disabled="!hasPreviousPage || isLoading"
        class="px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        @click="emit('page-change', currentPage - 1)"
      >
        {{ $t('common.previous') }}
      </button>

      <button
        :disabled="!hasNextPage || isLoading"
        class="px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        @click="emit('page-change', currentPage + 1)"
      >
        {{ $t('common.next') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  currentPage: number;
  totalPages: number;
  totalCount: number;
  isLoading: boolean;
  hasNextPage: boolean;
  hasPreviousPage: boolean;
}

defineProps<Props>();

const emit = defineEmits<{
  'page-change': [pageNumber: number];
}>();
</script>

<style scoped></style>
