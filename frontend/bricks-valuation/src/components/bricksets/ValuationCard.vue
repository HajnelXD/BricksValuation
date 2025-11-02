<script setup lang="ts">
/**
 * ValuationCard Component
 * Karta pojedynczej wyceny prezentująca wartość, komentarz, lajki i akcje
 *
 * Features:
 * - Displays valuation with formatted value and relative timestamp
 * - Expandable comment section with truncation
 * - Integrated like button with optimistic updates
 * - Like functionality via useLikeValuation composable
 * - User info display
 *
 * Props:
 * - valuation: ValuationViewModel with all valuation data
 * - canLike: Whether current user can like (should be true if not author)
 * - currentUserId: ID of current user (null if not authenticated)
 * - isLikedByMe: Whether current user has already liked this valuation (optional)
 */

import { ref, computed } from 'vue';
import type { ValuationViewModel } from '@/types/bricksets';
import { useLikeValuation } from '@/composables/useLikeValuation';
import { useNotificationStore } from '@/stores/notification';
import LikeButton from './LikeButton.vue';

const props = defineProps<{
  valuation: ValuationViewModel;
  canLike: boolean;
  currentUserId: number | null;
  isLikedByMe?: boolean;
}>();

const emit = defineEmits<{
  like: [valuationId: number];
  'valuation-liked': [valuationId: number, newLikesCount: number];
  'like-error': [error: string];
}>();

const isExpanded = ref(false);
const notificationStore = useNotificationStore();
const MAX_COMMENT_LENGTH = 200;

// Initialize like composable
const likeComposable = useLikeValuation(props.currentUserId, props.valuation.userId);

// Track likes count locally (for optimistic updates)
const localLikesCount = ref(props.valuation.likesCount);
const isLiked = ref(props.isLikedByMe ?? false);

// Computed: Check if button should be disabled
const isDisabled = computed(() => {
  // Disabled if not authenticated or user is author
  return props.currentUserId === null || props.currentUserId === props.valuation.userId;
});

// Computed: Check if comment should be truncated
const shouldTruncate = computed(() => {
  return props.valuation.comment.length > MAX_COMMENT_LENGTH;
});

// Computed: Display comment with truncation logic
const displayedComment = computed(() => {
  if (isExpanded.value || !shouldTruncate.value) {
    return props.valuation.comment;
  }
  return props.valuation.comment.slice(0, MAX_COMMENT_LENGTH) + '...';
});

/**
 * Toggle comment expand/collapse state
 */
function toggleExpand() {
  isExpanded.value = !isExpanded.value;
}

/**
 * Handle like button click
 * Calls useLikeValuation composable with optimistic updates and error handling
 */
async function handleLike() {
  // Early exit if button should be disabled
  if (isDisabled.value) {
    if (props.currentUserId === null) {
      notificationStore.addNotification('Musisz być zalogowany aby polajkować wycenę', 'error');
    } else {
      notificationStore.addNotification('Nie możesz polajkować własnej wyceny', 'error');
    }
    return;
  }

  try {
    // Call composable to handle like operation
    await likeComposable.toggleLike(props.valuation.id);

    // Update local state to match composable state
    isLiked.value = likeComposable.isLiked.value;
    localLikesCount.value = likeComposable.currentLikesCount.value;

    // Emit success event for parent component
    emit('valuation-liked', props.valuation.id, localLikesCount.value);

    // Show success notification
    notificationStore.addNotification('Wycena została polajkowana!', 'success');

    // Emit legacy event for backwards compatibility
    emit('like', props.valuation.id);
  } catch (error) {
    // Composable has already rolled back state
    const errorMessage = error instanceof Error ? error.message : 'Nie udało się polajkować wyceny';

    // Show error notification
    notificationStore.addNotification(errorMessage, 'error');

    // Emit error event for parent component
    emit('like-error', errorMessage);
  }
}
</script>

<template>
  <div
    class="bg-gray-800 border border-gray-700 rounded-lg p-5 hover:border-gray-600 transition-colors dark:bg-gray-900 dark:border-gray-700"
    role="article"
  >
    <!-- Header: Value and Timestamp -->
    <div class="flex items-start justify-between mb-3 flex-wrap gap-2">
      <div>
        <p class="text-2xl font-bold text-white">{{ valuation.valueFormatted }}</p>
        <p class="text-gray-400 text-sm mt-1">{{ valuation.createdAtRelative }}</p>
      </div>
      <div class="flex items-center gap-2">
        <LikeButton
          :likes-count="localLikesCount"
          :disabled="isDisabled"
          :loading="likeComposable.isLiking.value"
          :is-liked="isLiked"
          @like="handleLike"
        />
      </div>
    </div>

    <!-- Comment -->
    <div v-if="valuation.comment" class="mb-3">
      <p class="text-gray-300 text-sm leading-relaxed whitespace-pre-wrap">
        {{ displayedComment }}
      </p>
      <button
        v-if="shouldTruncate"
        type="button"
        class="text-blue-400 text-sm font-semibold mt-2 hover:text-blue-300 underline focus:outline-none focus:ring-2 focus:ring-blue-400 rounded px-1"
        @click="toggleExpand"
      >
        {{ isExpanded ? $t('bricksets.detail.showLess') : $t('bricksets.detail.showMore') }}
      </button>
    </div>

    <!-- User Info -->
    <p class="text-gray-500 text-xs">
      {{ $t('bricksets.detail.by') }} {{ $t('bricksets.detail.user') }} #{{ valuation.userId }}
    </p>
  </div>
</template>

<style scoped>
@media (prefers-reduced-motion: reduce) {
  /* Disable animations for users who prefer reduced motion */
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
</style>
