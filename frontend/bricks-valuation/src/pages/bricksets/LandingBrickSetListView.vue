<script setup lang="ts">
/**
 * LandingBrickSetListView
 * Public view for browsing and filtering BrickSet listings
 * Serves as homepage and public bricksets directory
 *
 * Orchestrates:
 * - useBrickSetListSearch composable (API, state, watchers)
 * - Sub-components (filters panel, list, pagination, empty/error states)
 * - Query param synchronization
 * - Accessibility features
 */

import { computed, watchEffect, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import type { BrickSetFiltersState } from '@/types/bricksets';
import { validateOrderingOption, parseBooleanQueryParam } from '@/mappers/bricksets';
import { useBrickSetListSearch, buildQueryParams } from '@/composables/useBrickSetListSearch';
import BrickSetFiltersPanel from '@/components/bricksets/BrickSetFiltersPanel.vue';
import BrickSetCard from '@/components/bricksets/BrickSetCard.vue';
import LoadingSkeletons from '@/components/bricksets/LoadingSkeletons.vue';
import Pagination from '@/components/bricksets/Pagination.vue';
import EmptyState from '@/components/bricksets/EmptyState.vue';
import ErrorState from '@/components/bricksets/ErrorState.vue';

const router = useRouter();
const route = useRoute();

/**
 * Initialize filters from URL query parameters
 */
function initializeFiltersFromQuery(): Partial<BrickSetFiltersState> {
  const query = route.query;

  return {
    q: (query.q as string) || '',
    production_status: (query.production_status as any) || null,
    completeness: (query.completeness as any) || null,
    has_instructions: parseBooleanQueryParam(query.has_instructions as string),
    has_box: parseBooleanQueryParam(query.has_box as string),
    is_factory_sealed: parseBooleanQueryParam(query.is_factory_sealed as string),
    ordering: validateOrderingOption(query.ordering),
    page: Math.max(1, parseInt(String(query.page || 1))),
  };
}

// Initialize composable with filters from URL
const { items, count, loading, error, filters, setFilters, resetFilters, fetch } =
  useBrickSetListSearch({
    initialFilters: initializeFiltersFromQuery(),
  });

// Computed properties
const totalPages = computed(() => Math.ceil(count / (filters.pageSize || 20)));
const hasResults = computed(() => items.length > 0);
const isEmpty = computed(() => !loading && count === 0);
const hasError = computed(() => error !== null && error !== '');

/**
 * Synchronize filters to query parameters
 * Uses router.replace to avoid history spam
 */
watchEffect(() => {
  const newQuery = buildQueryParams(filters);
  const queryString = JSON.stringify(newQuery);
  const currentString = JSON.stringify(route.query);

  if (queryString !== currentString) {
    router.replace({ query: newQuery });
  }
});

/**
 * Event handlers
 */
function handleFiltersUpdate(updates: Partial<BrickSetFiltersState>) {
  setFilters(updates);
}

function handleFiltersReset() {
  resetFilters();
}

function handlePageChange(newPage: number) {
  setFilters({ page: newPage });
  // Scroll to top of list for accessibility
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function handleCardClick(id: number) {
  router.push(`/bricksets/${id}`);
}

function handleRetry() {
  fetch();
}

function handleEmptyStateReset() {
  resetFilters();
}

// Trigger initial fetch on component mount (not in setup to allow async initialization)
onMounted(() => {
  fetch();
});
</script>

<template>
  <main class="min-h-screen bg-gray-50">
    <!-- Auth Prompt Banner -->
    <div class="bg-blue-50 border-b border-blue-200 py-3 px-4">
      <div class="max-w-7xl mx-auto text-sm text-blue-900">
        💡 {{ $t('bricksets.authPrompt') }}
        <router-link to="/login" class="font-semibold underline hover:no-underline">
          {{ $t('nav.login') }}
        </router-link>
      </div>
    </div>

    <!-- Main Content Container -->
    <div class="max-w-7xl mx-auto px-4 py-8">
      <div class="flex flex-col gap-6">
        <!-- Header -->
        <div class="flex flex-col gap-2">
          <h1 class="text-3xl font-bold text-gray-900">
            {{ $t('bricksets.title') }}
          </h1>
          <p class="text-gray-600">
            {{ count }} {{ $t('bricksets.subtitle') }}
          </p>
        </div>

        <!-- Filters and List Layout -->
        <div class="flex gap-6 flex-col lg:flex-row">
          <!-- Filters Panel Component -->
          <aside class="w-full lg:w-64 flex-shrink-0">
            <BrickSetFiltersPanel
              :model-value="filters"
              :disabled="loading"
              @update:model-value="handleFiltersUpdate"
              @reset="handleFiltersReset"
            />
          </aside>

          <!-- Main Content -->
          <div class="flex-1">
            <!-- Loading State -->
            <LoadingSkeletons
              v-if="loading && !hasResults"
              :count="6"
            />

            <!-- Error State Component -->
            <ErrorState
              v-else-if="hasError"
              :error="error"
              @retry="handleRetry"
            />

            <!-- Empty State Component -->
            <EmptyState
              v-else-if="isEmpty"
              @reset-filters="handleEmptyStateReset"
            />

            <!-- List -->
            <div v-else class="space-y-4">
              <ul role="list" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <BrickSetCard
                  v-for="item in items"
                  :key="item.id"
                  :item="item"
                  @click="handleCardClick"
                />
              </ul>

              <!-- Pagination Component -->
              <Pagination
                :count="count"
                :page="filters.page"
                :page-size="filters.pageSize"
                :loading="loading"
                @update:page="handlePageChange"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<style scoped>
/* Smooth transitions */
main {
  transition: all 0.2s ease-in-out;
}
</style>
