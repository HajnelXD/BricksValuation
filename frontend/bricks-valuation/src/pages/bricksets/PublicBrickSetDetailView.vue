<script setup lang="ts">
/**
 * PublicBrickSetDetailView
 * Widok publiczny szczegółów zestawu z wycenami
 * Dostępny dla wszystkich (zalogowani i niezalogowani)
 *
 * Orchestrates:
 * - useBrickSetDetail composable (API, state)
 * - useAuthStore (sprawdzenie czy użytkownik zalogowany)
 * - Sub-components (header, stats, valuations, like button)
 * - Obsługa lajkowania wycen
 */

import { computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useBrickSetDetail } from '@/composables/useBrickSetDetail';
import { useAuthStore } from '@/stores/auth';
import { useNotificationStore } from '@/stores/notification';
import BrickSetHeader from '@/components/bricksets/BrickSetHeader.vue';
import BrickSetStats from '@/components/bricksets/BrickSetStats.vue';
import TopValuationHighlight from '@/components/bricksets/TopValuationHighlight.vue';
import ValuationCard from '@/components/bricksets/ValuationCard.vue';
import ValuationFormCard from '@/components/bricksets/ValuationFormCard.vue';
import AuthPromptBanner from '@/components/auth/AuthPromptBanner.vue';
import ErrorState from '@/components/bricksets/ErrorState.vue';
import LoadingSkeletons from '@/components/bricksets/LoadingSkeletons.vue';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const notificationStore = useNotificationStore();

const { brickSet, loading, error, fetchBrickSet, likeValuation } = useBrickSetDetail();

// Computed properties
const brickSetId = computed(() => {
  const id = route.params.id;
  return typeof id === 'string' ? Number.parseInt(id, 10) : null;
});

const hasValuations = computed(() => {
  return brickSet.value && brickSet.value.valuations.length > 0;
});

/**
 * Check if current authenticated user has already added a valuation
 */
const userValuationExists = computed(() => {
  if (!authStore.isAuthenticated || !brickSet.value) {
    return false;
  }

  return brickSet.value.valuations.some((v: { userId: number }) => v.userId === authStore.user?.id);
});

/**
 * Determine if form should be shown
 * Show form only if user is authenticated and doesn't have a valuation yet
 */
const showValuationForm = computed(() => {
  return authStore.isAuthenticated && !userValuationExists.value;
});

const headerViewModel = computed(() => {
  if (!brickSet.value) return null;

  return {
    number: brickSet.value.number,
    productionStatusLabel: brickSet.value.productionStatusLabel,
    completenessLabel: brickSet.value.completenessLabel,
    hasInstructions: brickSet.value.hasInstructions,
    hasBox: brickSet.value.hasBox,
    isFactorySealed: brickSet.value.isFactorySealed,
    ownerInitialEstimate: brickSet.value.ownerInitialEstimate,
    createdAtRelative: brickSet.value.createdAtRelative,
  };
});

const statsViewModel = computed(() => {
  if (!brickSet.value) return null;

  return {
    valuationsCount: brickSet.value.valuationsCount,
    totalLikes: brickSet.value.totalLikes,
  };
});

/**
 * Handle valuation creation - refresh brickset data to show new valuation
 */
function handleValuationCreated(): void {
  if (!brickSetId.value) return;

  // Show success notification
  notificationStore.addNotification({
    type: 'success',
    message: 'Wycena została dodana!',
  });

  // Refresh brickset data from API to get updated valuations list
  fetchBrickSet(brickSetId.value);

  // Scroll to valuations section
  setTimeout(() => {
    const valuationsSection = document.getElementById('valuations-section');
    if (valuationsSection) {
      valuationsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }, 100);
}

/**
 * Handle like valuation action
 */
async function handleLikeValuation(valuationId: number) {
  if (!authStore.isAuthenticated) {
    notificationStore.addNotification({
      type: 'error',
      message: 'Musisz być zalogowany, aby polajkować wycenę',
    });
    return;
  }

  try {
    await likeValuation(valuationId);
    notificationStore.addNotification({
      type: 'success',
      message: 'Wycena została polajkowana!',
    });
  } catch (err: unknown) {
    const errorMessage = err instanceof Error ? err.message : 'Błąd podczas polajkowania wyceny';
    notificationStore.addNotification({
      type: 'error',
      message: errorMessage,
    });
  }
}

/**
 * Handle retry on error
 */
function handleRetry() {
  if (brickSetId.value) {
    fetchBrickSet(brickSetId.value);
  }
}

/**
 * Handle back navigation
 */
function handleGoBack() {
  router.push('/');
}

/**
 * Handle edit navigation
 */
function handleEditBrickSet() {
  if (brickSetId.value) {
    router.push({ name: 'brickset-edit', params: { id: brickSetId.value } });
  }
}

/**
 * Handle top valuation click - scroll to valuations section
 */
function handleTopValuationClick() {
  const valuationsSection = document.getElementById('valuations-section');
  if (valuationsSection) {
    valuationsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
}

// Fetch BrickSet on mount
onMounted(() => {
  if (brickSetId.value) {
    fetchBrickSet(brickSetId.value);
  } else {
    router.push('/');
  }
});
</script>

<template>
  <main class="min-h-screen bg-gray-900">
    <div class="max-w-4xl mx-auto px-4 py-8">
      <!-- Back Button and Edit Button -->
      <div class="mb-4 flex gap-2">
        <button
          type="button"
          class="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-gray-500"
          @click="handleGoBack"
        >
          ← {{ $t('bricksets.detail.back') }}
        </button>
        <button
          v-if="authStore.isAuthenticated"
          type="button"
          class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
          @click="handleEditBrickSet"
        >
          ✎ {{ $t('bricksets.detail.edit') }}
        </button>
      </div>

      <!-- Loading State -->
      <LoadingSkeletons v-if="loading && !brickSet" :count="3" />

      <!-- Error State -->
      <ErrorState v-else-if="error" :error="error" @retry="handleRetry" />

      <!-- Main Content -->
      <div v-else-if="brickSet" class="space-y-6">
        <!-- Auth Prompt Banner for non-authenticated users -->
        <AuthPromptBanner v-if="!authStore.isAuthenticated" />

        <!-- BrickSet Header -->
        <BrickSetHeader v-if="headerViewModel" :header="headerViewModel" />

        <!-- BrickSet Stats -->
        <BrickSetStats v-if="statsViewModel" :stats="statsViewModel" />

        <!-- Top Valuation Highlight -->
        <TopValuationHighlight
          v-if="brickSet.topValuation"
          :valuation="brickSet.topValuation"
          @click="handleTopValuationClick"
        />

        <!-- Valuation Form (Inline) -->
        <ValuationFormCard
          v-if="showValuationForm && brickSetId"
          :brickset-id="brickSetId"
          @valuation-created="handleValuationCreated"
        />

        <!-- Valuations Section -->
        <div id="valuations-section" class="space-y-4">
          <h2 class="text-2xl font-bold text-white">
            {{ $t('bricksets.detail.valuations') }}
          </h2>

          <!-- Empty Valuations State -->
          <div
            v-if="!hasValuations"
            class="bg-gray-800 border border-gray-700 rounded-lg p-8 text-center"
          >
            <p class="text-gray-400 text-lg">
              {{ $t('bricksets.detail.noValuations') }}
            </p>
            <p class="text-gray-500 text-sm mt-2">
              {{ $t('bricksets.detail.beFirst') }}
            </p>
          </div>

          <!-- Valuations List -->
          <div v-else class="space-y-4">
            <ValuationCard
              v-for="valuation in brickSet.valuations"
              :key="valuation.id"
              :valuation="valuation"
              :can-like="authStore.isAuthenticated"
              :current-user-id="authStore.user?.id ?? null"
              @like="handleLikeValuation"
            />
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
