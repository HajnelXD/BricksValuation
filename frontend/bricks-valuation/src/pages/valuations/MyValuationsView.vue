<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <div class="container mx-auto px-4 py-8 max-w-6xl">
      <!-- Header -->
      <MyValuationsHeader :total-valuations="pagination.totalCount" :total-likes="totalLikes" />

      <!-- Main content -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 md:p-8">
        <!-- Loading state -->
        <div v-if="loading && isEmpty" class="space-y-4">
          <LoadingSkeletons :count="2" />
        </div>

        <!-- Error state -->
        <ErrorState v-else-if="error" :error="error" :is-loading="loading" @retry="handleRetry" />

        <!-- Empty state -->
        <EmptyState v-else-if="isEmpty" />

        <!-- Data state -->
        <template v-else>
          <MyValuationsGrid
            :valuations="valuations"
            @navigate-to-brickset="handleNavigateToBrickset"
          />

          <!-- Pagination -->
          <PaginationControls
            :current-page="pagination.currentPage"
            :total-pages="pagination.totalPages"
            :total-count="pagination.totalCount"
            :is-loading="loading"
            :has-next-page="pagination.hasNextPage"
            :has-previous-page="pagination.hasPreviousPage"
            @page-change="handlePageChange"
          />
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { useMyValuesList } from '@/composables/useMyValuesList';
import type { OwnValuationViewModel } from '@/types/bricksets';
import MyValuationsHeader from '@/components/valuations/MyValuationsHeader.vue';
import MyValuationsGrid from '@/components/valuations/MyValuationsGrid.vue';
import PaginationControls from '@/components/valuations/PaginationControls.vue';
import EmptyState from '@/components/valuations/EmptyState.vue';
import ErrorState from '@/components/valuations/ErrorState.vue';
import LoadingSkeletons from '@/components/bricksets/LoadingSkeletons.vue';

const router = useRouter();

// Use composable
const { valuations, loading, error, pagination, isEmpty, refresh, goToPage } = useMyValuesList();

// Computed: total likes across all valuations
const totalLikes = computed(() => {
  return valuations.value.reduce(
    (sum: number, valuation: OwnValuationViewModel) => sum + valuation.likesCount,
    0
  );
});

/**
 * Handle page change from pagination controls
 */
function handlePageChange(pageNumber: number) {
  // Validate page number
  if (pageNumber >= 1 && pageNumber <= pagination.value.totalPages) {
    goToPage(pageNumber);
  }
}

/**
 * Handle navigation to brickset detail
 */
function handleNavigateToBrickset(bricksetId: number) {
  router.push(`/bricksets/${bricksetId}`);
}

/**
 * Handle retry on error
 */
function handleRetry() {
  refresh();
}
</script>

<style scoped></style>
