<script setup lang="ts">
/**
 * PaginationControls Component
 * Navigation between pages of My BrickSets list
 * Shows: Previous button, page numbers, Next button
 */

import { computed } from 'vue';

interface Props {
  currentPage: number;
  totalCount: number;
  pageSize: number;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  'page-change': [page: number];
}>();

const totalPages = computed(() => Math.ceil(props.totalCount / props.pageSize));
const pages = computed(() => {
  const pagesList: number[] = [];
  const maxPagesToShow = 5;

  if (totalPages.value <= maxPagesToShow) {
    // Show all pages if total is small
    for (let i = 1; i <= totalPages.value; i++) {
      pagesList.push(i);
    }
  } else {
    // Show smart pagination: 1, 2, 3, ..., totalPages-1, totalPages
    const isNearStart = props.currentPage <= 3;
    const isNearEnd = props.currentPage > totalPages.value - 3;

    if (isNearStart) {
      for (let i = 1; i <= 4; i++) {
        pagesList.push(i);
      }
      pagesList.push(-1); // -1 means ellipsis
      pagesList.push(totalPages.value);
    } else if (isNearEnd) {
      pagesList.push(1);
      pagesList.push(-1);
      for (let i = totalPages.value - 3; i <= totalPages.value; i++) {
        pagesList.push(i);
      }
    } else {
      pagesList.push(1);
      pagesList.push(-1);
      for (let i = props.currentPage - 1; i <= props.currentPage + 1; i++) {
        pagesList.push(i);
      }
      pagesList.push(-1);
      pagesList.push(totalPages.value);
    }
  }

  return pagesList;
});

function goToPage(page: number) {
  if (page >= 1 && page <= totalPages.value) {
    emit('page-change', page);
  }
}

function previousPage() {
  if (props.currentPage > 1) {
    emit('page-change', props.currentPage - 1);
  }
}

function nextPage() {
  if (props.currentPage < totalPages.value) {
    emit('page-change', props.currentPage + 1);
  }
}
</script>

<template>
  <div v-if="totalPages > 1" class="flex items-center justify-center gap-2 mt-6">
    <!-- Previous Button -->
    <button
      @click="previousPage"
      :disabled="currentPage === 1"
      class="px-3 py-2 rounded-lg border border-gray-600 text-gray-300 hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
    >
      {{ $t('common.previous') }}
    </button>

    <!-- Page Numbers -->
    <div class="flex gap-1">
      <button
        v-for="page in pages"
        :key="page"
        @click="page > 0 && goToPage(page)"
        :disabled="page === -1"
        :class="[
          'px-3 py-2 rounded-lg transition-colors',
          page === -1
            ? 'cursor-default text-gray-500'
            : page === currentPage
            ? 'bg-blue-600 text-white'
            : 'border border-gray-600 text-gray-300 hover:bg-gray-700',
        ]"
      >
        {{ page === -1 ? '...' : page }}
      </button>
    </div>

    <!-- Next Button -->
    <button
      @click="nextPage"
      :disabled="currentPage === totalPages"
      class="px-3 py-2 rounded-lg border border-gray-600 text-gray-300 hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
    >
      {{ $t('common.next') }}
    </button>
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
</style>
