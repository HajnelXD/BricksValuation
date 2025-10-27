<script setup lang="ts">
/**
 * AuthenticatedBrickSetListView
 * View for authenticated users to manage their BrickSet collection
 * Allows viewing, filtering, and managing owned bricksets
 *
 * Orchestrates:
 * - User's owned bricksets list
 * - Filtering and search functionality
 * - BrickSet management actions (view, edit, delete)
 * - Navigation and authentication checks
 */

import { computed, watchEffect, ref, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import type { BrickSetFiltersState, ProductionStatus, Completeness } from '@/types/bricksets';
import { validateOrderingOption, parseBooleanQueryParam } from '@/mappers/bricksets';
import { useBrickSetListSearch, buildQueryParams } from '@/composables/useBrickSetListSearch';
import { env } from '@/config/env';
import BrickSetFiltersPanel from '@/components/bricksets/BrickSetFiltersPanel.vue';
import BrickSetCard from '@/components/bricksets/BrickSetCard.vue';
import LoadingSkeletons from '@/components/bricksets/LoadingSkeletons.vue';
import Pagination from '@/components/bricksets/Pagination.vue';
import EmptyState from '@/components/bricksets/EmptyState.vue';
import ErrorState from '@/components/bricksets/ErrorState.vue';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

const PRODUCTION_STATUS_VALUES: readonly ProductionStatus[] = ['ACTIVE', 'RETIRED'];
const COMPLETENESS_VALUES: readonly Completeness[] = ['COMPLETE', 'INCOMPLETE'];

function normalizeQueryParam(param: unknown): string | undefined {
  if (Array.isArray(param)) {
    return typeof param[0] === 'string' ? param[0] : undefined;
  }
  return typeof param === 'string' ? param : undefined;
}

function parseEnumQuery<T extends string>(
  value: string | undefined,
  allowed: readonly T[]
): T | null {
  if (!value) {
    return null;
  }
  return allowed.includes(value as T) ? (value as T) : null;
}

/**
 * Initialize filters from URL query parameters
 */
function initializeFiltersFromQuery(): Partial<BrickSetFiltersState> {
  const query = route.query;
  const productionStatusParam = normalizeQueryParam(query.production_status);
  const completenessParam = normalizeQueryParam(query.completeness);
  const orderingParam = normalizeQueryParam(query.ordering);
  const pageParam = normalizeQueryParam(query.page);
  const hasInstructionsParam = normalizeQueryParam(query.has_instructions);
  const hasBoxParam = normalizeQueryParam(query.has_box);
  const isFactorySealedParam = normalizeQueryParam(query.is_factory_sealed);

  return {
    q: normalizeQueryParam(query.q) || '',
    production_status: parseEnumQuery(productionStatusParam, PRODUCTION_STATUS_VALUES),
    completeness: parseEnumQuery(completenessParam, COMPLETENESS_VALUES),
    has_instructions: parseBooleanQueryParam(hasInstructionsParam),
    has_box: parseBooleanQueryParam(hasBoxParam),
    is_factory_sealed: parseBooleanQueryParam(isFactorySealedParam),
    ordering: validateOrderingOption(orderingParam),
    page: Math.max(1, Number.parseInt(pageParam ?? '1', 10) || 1),
  };
}

// Initialize composable with filters from URL
const { items, count, loading, error, filters, setFilters, resetFilters, fetch } =
  useBrickSetListSearch({
    initialFilters: initializeFiltersFromQuery(),
    endpoint: `/v${env.api.version}/users/me/bricksets`,
  });

const showFiltersPanel = ref(false);

/**
 * Synchronize filters to query parameters
 * Uses router.replace to avoid history spam
 */
watchEffect(() => {
  const newQuery = buildQueryParams(filters.value);
  const queryString = JSON.stringify(newQuery);
  const currentString = JSON.stringify(route.query);

  if (queryString !== currentString) {
    router.replace({ query: newQuery });
  }
});

watch(
  () => authStore.isAuthenticated,
  (isAuthenticated: boolean) => {
    if (!isAuthenticated) {
      router.push({ name: 'public-bricksets' });
    }
  }
);

/**
 * Event handlers
 */
function handleFiltersUpdate(updates: Partial<BrickSetFiltersState>) {
  setFilters(updates);
}

function handleFiltersReset() {
  resetFilters();
}

const noResultsFound = computed(() => {
  return !loading.value && count.value === 0 && !error.value;
});

const hasActiveFilters = computed(() => {
  const f = filters.value;
  return Boolean(
    f.q ||
      f.completeness ||
      f.production_status ||
      f.has_instructions ||
      f.has_box ||
      f.is_factory_sealed ||
      (f.ordering && f.ordering !== '-created_at')
  );
});

function handleBrickSetClick(brickSetId: number) {
  // TODO: Create BrickSetDetailView and enable this route
  console.log('BrickSet clicked:', brickSetId);
  // router.push({
  //   name: 'app-brickset-detail',
  //   params: { id: brickSetId },
  // });
}

// Trigger initial fetch on component mount
onMounted(() => {
  fetch();
});
</script>

<template>
  <div class="authenticated-brickset-list-view">
    <div class="view-header">
      <h1>{{ $t('pages.authenticatedBricksets.title', 'My BrickSets') }}</h1>
      <p class="subtitle">
        {{ $t('pages.authenticatedBricksets.subtitle', 'Manage your collection') }}
      </p>
    </div>

    <!-- Mobile filters toggle -->
    <div class="mobile-filters-toggle md:hidden mb-4">
      <button
        class="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        @click="showFiltersPanel = !showFiltersPanel"
      >
        {{
          showFiltersPanel
            ? $t('common.hideFilters', 'Hide Filters')
            : $t('common.showFilters', 'Show Filters')
        }}
      </button>
    </div>

    <div class="view-container">
      <!-- Filters Panel -->
      <aside
        :class="[
          'filters-panel',
          { 'hidden md:block': !showFiltersPanel },
          { block: showFiltersPanel },
        ]"
      >
        <BrickSetFiltersPanel
          :filters="filters.value"
          :has-active-filters="hasActiveFilters"
          @update:search="(val: string) => handleFiltersUpdate({ q: val })"
          @update:completeness="
            (val: Completeness | null) => handleFiltersUpdate({ completeness: val })
          "
          @update:production-status="
            (val: ProductionStatus | null) => handleFiltersUpdate({ production_status: val })
          "
          @update:ordering="
            (val: BrickSetFiltersState['ordering']) => handleFiltersUpdate({ ordering: val })
          "
          @clear-filters="handleFiltersReset"
        />
      </aside>

      <!-- Main Content -->
      <main class="main-content">
        <!-- Error State -->
        <ErrorState v-if="error.value" :error="error.value" @retry="() => fetch()" />

        <!-- Loading State -->
        <LoadingSkeletons v-else-if="loading.value" />

        <!-- Empty State -->
        <EmptyState
          v-else-if="noResultsFound"
          :has-active-filters="hasActiveFilters"
          message="No bricksets found"
          @clear-filters="handleFiltersReset"
        />

        <!-- Bricksets Grid -->
        <template v-else>
          <div class="results-info mb-6">
            <p class="text-gray-600">
              {{ $t('common.showing', 'Showing') }}
              <span class="font-semibold">{{ items.value.length }}</span>
              {{ $t('common.of', 'of') }}
              <span class="font-semibold">{{ count.value }}</span>
              {{ $t('common.results', 'results') }}
            </p>
          </div>

          <div class="bricksets-grid">
            <BrickSetCard
              v-for="brickset in items.value"
              :key="brickset.id"
              :brickset="brickset"
              @click="handleBrickSetClick(brickset.id)"
            />
          </div>

          <!-- Pagination -->
          <Pagination
            :current-page="filters.value.page"
            :total-count="count.value"
            :page-size="filters.value.pageSize"
            @page-change="(page: number) => handleFiltersUpdate({ page })"
          />
        </template>
      </main>
    </div>
  </div>
</template>

<style scoped>
.authenticated-brickset-list-view {
  min-height: 100vh;
  background-color: #f9fafb;
  padding: 2rem 1rem;
}

.view-header {
  margin-bottom: 2rem;
}

.view-header h1 {
  font-size: 2rem;
  font-weight: bold;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #6b7280;
  font-size: 1rem;
}

.view-container {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

@media (min-width: 768px) {
  .view-container {
    grid-template-columns: 280px 1fr;
  }
}

.filters-panel {
  background-color: white;
  border-radius: 0.5rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  height: fit-content;
  position: sticky;
  top: 1rem;
}

.main-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.results-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.bricksets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
}

@media (max-width: 640px) {
  .bricksets-grid {
    grid-template-columns: 1fr;
  }
}

.mobile-filters-toggle button {
  font-weight: 500;
}
</style>
