<script setup lang="ts">
/**
 * AuthPromptBanner Component
 * Banner informacyjny dla niezalogowanych użytkowników z wezwaniem do zalogowania
 */
</script>

<template>
  <div
    class="bg-blue-900 border border-blue-700 rounded-lg p-4 mb-6 text-center"
    role="banner"
    aria-label="Zaloguj się aby uzyskać pełny dostęp"
  >
    <p class="text-blue-100 mb-3">
      {{ $t('auth.prompt.message') }}
    </p>
    <div class="flex gap-3 justify-center flex-wrap">
      <router-link
        to="/login"
        class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-blue-400"
      >
        {{ $t('auth.prompt.login') }}
      </router-link>
      <router-link
        to="/register"
        class="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-gray-400"
      >
        {{ $t('auth.prompt.register') }}
      </router-link>
    </div>
  </div>
</template>

<style scoped></style>
