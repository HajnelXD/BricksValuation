<script setup lang="ts">
/**
 * ValuationCard Component
 * Karta pojedynczej wyceny prezentująca wartość, komentarz, lajki i akcje
 */

import { ref } from 'vue';
import type { ValuationViewModel } from '@/types/bricksets';
import LikeButton from './LikeButton.vue';

const props = defineProps<{
  valuation: ValuationViewModel;
  canLike: boolean;
  currentUserId: number | null;
}>();

const emit = defineEmits<{
  like: [valuationId: number];
}>();

const isLiking = ref(false);
const isExpanded = ref(false);
const MAX_COMMENT_LENGTH = 200;

const isDisabled = (): boolean => {
  // Disabled jeśli użytkownik jest autorem wyceny
  return props.currentUserId === props.valuation.userId;
};

const shouldTruncate = (): boolean => {
  return props.valuation.comment.length > MAX_COMMENT_LENGTH;
};

const displayedComment = (): string => {
  if (isExpanded.value || !shouldTruncate()) {
    return props.valuation.comment;
  }
  return props.valuation.comment.slice(0, MAX_COMMENT_LENGTH) + '...';
};

function toggleExpand() {
  isExpanded.value = !isExpanded.value;
}

async function handleLike() {
  if (!props.canLike || isDisabled()) return;

  isLiking.value = true;
  try {
    emit('like', props.valuation.id);
    // W rzeczywistości handler w composable/parent musi obsłużyć API call
  } finally {
    // Loading state będzie zarządzany przez parent po zakończeniu API call
    setTimeout(() => {
      isLiking.value = false;
    }, 500);
  }
}
</script>

<template>
  <div
    class="bg-gray-800 border border-gray-700 rounded-lg p-5 hover:border-gray-600 transition-colors"
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
          :likes-count="valuation.likesCount"
          :disabled="!canLike || isDisabled()"
          :loading="isLiking"
          @like="handleLike"
        />
      </div>
    </div>

    <!-- Comment -->
    <div v-if="valuation.comment" class="mb-3">
      <p class="text-gray-300 text-sm leading-relaxed whitespace-pre-wrap">
        {{ displayedComment() }}
      </p>
      <button
        v-if="shouldTruncate()"
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

<style scoped></style>
