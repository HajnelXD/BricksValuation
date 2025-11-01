<script setup lang="ts">
/**
 * MyBrickSetsView
 * User's personal view of their own bricksets
 * Displays list with pagination, sorting, and edit capabilities
 *
 * Features:
 * - List of user's bricksets with metrics
 * - Sorting by creation date, number of valuations, or likes
 * - Pagination with smart page navigation
 * - Quick edit and navigation to brickset details
 * - Empty state when no bricksets
 * - Error handling and retry
 */

import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import type { SortOption, SortOrderingValue } from '@/types/bricksets';
import { useMyBrickSetsList } from '@/composables/useMyBrickSetsList';
import OwnedBrickSetList from '@/components/myBricksets/OwnedBrickSetList.vue';
import SortControl from '@/components/myBricksets/SortControl.vue';
import PaginationControls from '@/components/myBricksets/PaginationControls.vue';
import ErrorState from '@/components/bricksets/ErrorState.vue';

const router = useRouter();
const { t } = useI18n();

// Use composable
console.log('[MyBrickSetsView] About to call useMyBrickSetsList');
let composableResult;
try {
  composableResult = useMyBrickSetsList();
  console.log('[MyBrickSetsView] Composable called successfully');
} catch (e) {
  console.error('[MyBrickSetsView] Error calling composable:', e);
  throw e;
}

if (!composableResult) {
  console.error('[MyBrickSetsView] Composable returned undefined or null!');
  throw new Error('useMyBrickSetsList returned undefined');
}

const { bricksets, totalCount, isLoading, error, filters, changePage, changeSorting, refreshList } =
  composableResult;

console.log('[MyBrickSetsView] Destructured from composable:', {
  bricksets,
  totalCount,
  isLoading,
  error,
  filters,
});
console.log('[MyBrickSetsView] bricksets.value:', bricksets?.value);
console.log('[MyBrickSetsView] totalCount.value:', totalCount?.value);
console.log('[MyBrickSetsView] isLoading.value:', isLoading?.value);

// Sort options with i18n labels
const sortOptions = computed<SortOption[]>(() => [
  {
    value: '-created_at',
    label: t('myBrickSets.sort.createdAt'),
  },
  {
    value: '-valuations',
    label: t('myBrickSets.sort.valuations'),
  },
  {
    value: '-likes',
    label: t('myBrickSets.sort.likes'),
  },
]);

// Computed properties
const hasError = computed(() => error.value !== null);

/**
 * Handle card click - navigate to brickset details
 */
function handleCardClick(bricksetId: number) {
  router.push(`/app/bricksets/${bricksetId}`);
}

/**
 * Handle edit click - navigate to brickset edit page
 */
function handleEditClick(bricksetId: number) {
  router.push(`/app/my/bricksets/${bricksetId}/edit`);
}

/**
 * Handle sort change
 */
function handleSortChange(newOrdering: SortOrderingValue) {
  changeSorting(newOrdering);
}

/**
 * Handle page change
 */
function handlePageChange(page: number) {
  changePage(page);
}

/**
 * Handle retry after error
 */
function handleRetry() {
  refreshList();
}
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-white mb-2">{{ $t('myBrickSets.title') }}</h1>
      <p class="text-gray-400">{{ totalCount?.value ?? 0 }} {{ $t('bricksets.subtitle') }}</p>
    </div>

    <!-- Controls Section (only show once filters are initialized) -->
    <template v-if="filters && bricksets && isLoading">
      <div class="flex items-center justify-between gap-4 mb-6">
        <div>
          <SortControl :model-value="filters.ordering" :options="sortOptions" @update:model-value="handleSortChange" />
        </div>
      </div>

      <!-- Error State -->
      <div v-if="hasError" class="mb-6">
        <ErrorState :error="error.value?.message || 'Unknown error'" @retry="handleRetry" />
      </div>

      <!-- List Section -->
      <div v-else>
        <OwnedBrickSetList
          :bricksets="bricksets.value"
          :is-loading="isLoading.value"
          @card-click="handleCardClick"
          @edit-click="handleEditClick"
        />

        <!-- Pagination -->
        <PaginationControls
          :current-page="filters.page"
          :total-count="totalCount.value"
          :page-size="filters.page_size"
          @page-change="handlePageChange"
        />
      </div>
    </template>
  </div>
</template>

<style scoped>
.container {
  max-width: 1280px;
}
</style>
