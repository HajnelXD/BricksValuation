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

import { computed, watchEffect, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import type { BrickSetFiltersState, ProductionStatus, Completeness } from '@/types/bricksets';
import { validateOrderingOption, parseBooleanQueryParam } from '@/mappers/bricksets';
import { useBrickSetListSearch, buildQueryParams } from '@/composables/useBrickSetListSearch';
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

function parseEnumQuery<T extends string>(value: unknown, allowed: readonly T[]): T | null {
  if (typeof value !== 'string') {
    return null;
  }
  return allowed.includes(value as T) ? (value as T) : null;
}

function normalizeQueryParam(param: unknown): string | undefined {
  if (Array.isArray(param)) {
    return typeof param[0] === 'string' ? param[0] : undefined;
  }
  return typeof param === 'string' ? param : undefined;
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

  return {
    q: normalizeQueryParam(query.q) || '',
    production_status: parseEnumQuery(productionStatusParam, PRODUCTION_STATUS_VALUES),
    completeness: parseEnumQuery(completenessParam, COMPLETENESS_VALUES),
    has_instructions: parseBooleanQueryParam(normalizeQueryParam(query.has_instructions)),
    has_box: parseBooleanQueryParam(normalizeQueryParam(query.has_box)),
    is_factory_sealed: parseBooleanQueryParam(normalizeQueryParam(query.is_factory_sealed)),
    ordering: validateOrderingOption(orderingParam),
    page: Math.max(1, Number.parseInt(pageParam ?? '1', 10) || 1),
  };
}

// Initialize composable with filters from URL
const { items, count, loading, error, filters, setFilters, resetFilters, fetch } =
  useBrickSetListSearch({
    initialFilters: initializeFiltersFromQuery(),
  });

// Computed properties
const hasResults = computed(() => items.value.length > 0);
const isEmpty = computed(() => !loading.value && count.value === 0);
const hasError = computed(() => error.value !== null && error.value !== '');

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
  (isAuthenticated: boolean, wasAuthenticated: boolean | void) => {
    if (!isAuthenticated && wasAuthenticated) {
      fetch();
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

// Trigger initial fetch on component mount (not in setup to allow async initialization)
onMounted(() => {
  fetch();
});
</script>

<template>
  <main class="min-h-screen bg-gray-900">
    <!-- Auth Prompt Banner -->
    <div v-if="!authStore.isAuthenticated" class="bg-gray-800 border-b border-gray-700 py-3 px-4">
      <div class="max-w-7xl mx-auto text-sm text-gray-300">
        💡 {{ $t('bricksets.authPrompt') }}
        <router-link
          to="/login"
          class="font-semibold text-blue-400 hover:text-blue-300 underline hover:no-underline"
        >
          {{ $t('nav.login') }}
        </router-link>
        <br />
        <span class="inline-flex items-center gap-2">
          {{ $t('auth.noAccountPrompt') }}
          <router-link
            to="/register"
            class="font-semibold text-blue-400 hover:text-blue-300 underline hover:no-underline"
          >
            {{ $t('nav.register') }}
          </router-link>
        </span>
      </div>
    </div>

    <!-- Main Content Container -->
    <div class="max-w-7xl mx-auto px-4 py-8">
      <div class="flex flex-col gap-6">
        <!-- Header -->
        <div class="flex flex-col gap-2">
          <div class="flex items-center flex-col gap-4">
            <h1 class="text-3xl font-bold text-white w-fit">
              {{ $t('bricksets.title') }}
            </h1>
            <button
              v-if="authStore.isAuthenticated"
              class="flex-shrink-0 w-10 h-10 rounded-full bg-blue-600 hover:bg-blue-700 text-white font-bold text-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 focus:ring-blue-500 shadow-md hover:shadow-lg flex items-center justify-center"
              :aria-label="$t('bricksets.create.addNew')"
              title="Dodaj nowy zestaw"
              @click="() => router.push({ name: 'brickset-create' })"
            >
              +
            </button>
          </div>
          <p class="text-gray-400">{{ count }} {{ $t('bricksets.subtitle') }}</p>
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
            <LoadingSkeletons v-if="loading && !hasResults" :count="6" />

            <!-- Error State Component -->
            <ErrorState v-else-if="hasError" :error="error" @retry="handleRetry" />

            <!-- Empty State Component -->
            <EmptyState v-else-if="isEmpty" />

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
