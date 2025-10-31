<script setup lang="ts">
/**
 * TopValuationHighlight Component
 * Wyróżniona sekcja prezentująca najwyżej polajkowaną wycenę
 */

import { ref } from 'vue';
import type { TopValuationDetailViewModel } from '@/types/bricksets';

const props = defineProps<{
  valuation: TopValuationDetailViewModel | null;
}>();

const emit = defineEmits<{
  click: [valuationId: number];
}>();

const isExpanded = ref(false);
const MAX_COMMENT_LENGTH = 150;

const shouldTruncate = (): boolean => {
  return !!props.valuation && props.valuation.comment.length > MAX_COMMENT_LENGTH;
};

const displayedComment = (): string => {
  if (!props.valuation) return '';
  if (isExpanded.value || !shouldTruncate()) {
    return props.valuation.comment;
  }
  return props.valuation.comment.slice(0, MAX_COMMENT_LENGTH) + '...';
};

function toggleExpand() {
  isExpanded.value = !isExpanded.value;
}

function handleClick() {
  if (props.valuation) {
    emit('click', props.valuation.id);
  }
}
</script>

<template>
  <div
    v-if="valuation"
    class="bg-gradient-to-br from-yellow-900 to-yellow-800 border-2 border-yellow-600 rounded-lg p-6 mb-6 cursor-pointer hover:shadow-xl transition-shadow"
    role="article"
    tabindex="0"
    @click="handleClick"
    @keydown.enter="handleClick"
    @keydown.space.prevent="handleClick"
  >
    <!-- Trophy Icon and Badge -->
    <div class="flex items-center gap-3 mb-4">
      <span class="text-4xl" aria-label="Najlepsza wycena">🏆</span>
      <div>
        <h2 class="text-xl font-bold text-yellow-100">
          {{ $t('bricksets.detail.topValuation') }}
        </h2>
        <p class="text-yellow-200 text-sm">{{ valuation.createdAtRelative }}</p>
      </div>
    </div>

    <!-- Valuation Value -->
    <div class="mb-4">
      <p class="text-3xl font-bold text-white">{{ valuation.valueFormatted }}</p>
    </div>

    <!-- Likes Count -->
    <div class="mb-4">
      <p class="text-yellow-100 text-lg">
        ❤️ {{ valuation.likesCount }}
        {{ $t('bricksets.likes') }}
      </p>
    </div>

    <!-- Comment -->
    <div v-if="valuation.comment" class="mb-3">
      <p class="text-yellow-50 text-sm leading-relaxed whitespace-pre-wrap">
        {{ displayedComment() }}
      </p>
      <button
        v-if="shouldTruncate()"
        type="button"
        class="text-yellow-300 text-sm font-semibold mt-2 hover:text-yellow-100 underline focus:outline-none focus:ring-2 focus:ring-yellow-400 rounded px-1"
        @click.stop="toggleExpand"
      >
        {{ isExpanded ? $t('bricksets.detail.showLess') : $t('bricksets.detail.showMore') }}
      </button>
    </div>

    <!-- User Info -->
    <p class="text-yellow-200 text-xs">
      {{ $t('bricksets.detail.by') }} {{ $t('bricksets.detail.user') }} #{{ valuation.userId }}
    </p>
  </div>
</template>

<style scoped>
div[role='article']:focus-visible {
  outline: 2px solid #fbbf24;
  outline-offset: 2px;
}
</style>
