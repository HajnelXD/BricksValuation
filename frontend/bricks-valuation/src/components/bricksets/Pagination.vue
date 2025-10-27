<script setup lang="ts">
/**
 * Pagination Component
 * Displays pagination controls with previous/next buttons and page numbers
 */

import { computed } from 'vue';

interface Props {
  count: number;
  page: number;
  pageSize: number;
  loading?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
});

const emit = defineEmits<{
  'update:page': [page: number];
}>();

const totalPages = computed(() => Math.ceil(props.count / props.pageSize));
const pageNumbers = computed(() => {
  const pages = [];
  for (let i = 1; i <= totalPages.value; i++) {
    pages.push(i);
  }
  return pages;
});

function handlePageChange(newPage: number) {
  if (newPage >= 1 && newPage <= totalPages.value && !props.loading) {
    emit('update:page', newPage);
  }
}
</script>

<template>
  <div data-testid="pagination" class="flex justify-center items-center gap-2 mt-8" v-if="totalPages > 1">
    <!-- Previous Button -->
    <button
      @click="handlePageChange(page - 1)"
      :disabled="page === 1 || loading"
      data-testid="prev-page-btn"
      class="px-3 py-2 border border-gray-300 rounded-md text-sm disabled:opacity-50 hover:bg-gray-50 transition-colors"
      :aria-label="`Poprzednia strona`"
    >
      ← {{ $t('common.previous') }}
    </button>

    <!-- Page Numbers -->
    <div class="flex gap-1">
      <button
        v-for="pageNum in pageNumbers"
        :key="pageNum"
        @click="handlePageChange(pageNum)"
        :disabled="loading"
        :aria-current="page === pageNum ? 'page' : undefined"
        :aria-label="`Strona ${pageNum}`"
        :class="[
          'px-3 py-2 border rounded-md text-sm transition-colors',
          page === pageNum
            ? 'bg-blue-600 text-white border-blue-600'
            : 'border-gray-300 hover:bg-gray-100',
          'disabled:opacity-50',
        ]"
      >
        {{ pageNum }}
      </button>
    </div>

    <!-- Next Button -->
    <button
      @click="handlePageChange(page + 1)"
      :disabled="page >= totalPages || loading"
      data-testid="next-page-btn"
      class="px-3 py-2 border border-gray-300 rounded-md text-sm disabled:opacity-50 hover:bg-gray-50 transition-colors"
      :aria-label="`Następna strona`"
    >
      {{ $t('common.next') }} →
    </button>
  </div>
</template>

<style scoped></style>
