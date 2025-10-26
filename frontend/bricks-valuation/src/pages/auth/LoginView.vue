<script setup lang="ts">
/**
 * LoginView
 * Minimal placeholder for login functionality
 * Full implementation will be added later
 */

import { useRouter } from 'vue-router';

const router = useRouter();

function handleLoginClick() {
  // Placeholder - will be implemented later
  return;
}

function goToRegister() {
  router.push({ name: 'register' });
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 px-4">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-bold text-gray-900 dark:text-white">
          {{ $t('nav.login') }}
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
          Login functionality - coming soon
        </p>
      </div>

      <div class="mt-8 space-y-6">
        <button
          type="button"
          class="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors"
          @click="handleLoginClick"
        >
          {{ $t('nav.login') }}
        </button>

        <p class="text-center text-sm text-gray-600 dark:text-gray-400">
          {{ $t('auth.noAccountPrompt') }}
          <button
            type="button"
            class="font-semibold text-blue-600 dark:text-blue-400 hover:underline"
            @click="goToRegister"
          >
            {{ $t('nav.register') }}
          </button>
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Minimal styles - using Tailwind CSS */
</style>
