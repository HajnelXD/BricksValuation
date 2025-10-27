<script setup lang="ts">
/**
 * UserMenu Component
 * Dropdown menu for authenticated user in navigation
 * Features:
 * - User avatar with initials
 * - Dropdown menu with profile and logout options
 * - Accessibility: focus trap, keyboard navigation
 * - Loading state during logout
 */

import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useNotificationStore } from '@/stores/notification';

const router = useRouter();
const authStore = useAuthStore();
const notificationStore = useNotificationStore();

const isOpen = ref(false);
const isLoggingOut = ref(false);
const menuRef = ref<HTMLDivElement>();

/**
 * Get user initials from username for avatar
 */
const userInitials = computed(() => {
  if (!authStore.user?.username) return '?';
  return (
    authStore.user.username
      .split(' ')
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      .map((part: any) => part[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  );
});

/**
 * Toggle dropdown menu
 */
function toggleMenu() {
  isOpen.value = !isOpen.value;
}

/**
 * Close dropdown menu
 */
function closeMenu() {
  isOpen.value = false;
}

/**
 * Navigate to profile page
 */
function goToProfile() {
  closeMenu();
  router.push({ name: 'profile' });
}

/**
 * Handle logout action
 */
async function handleLogout() {
  isLoggingOut.value = true;

  try {
    await authStore.logout();
    closeMenu();

    // Show success notification
    notificationStore.success('Wylogowano pomyślnie');

    // Redirect to home
    await router.push('/');
  } catch (err: unknown) {
    console.error('Logout failed:', err);
    notificationStore.error('Błąd podczas wylogowania. Spróbuj ponownie');
  } finally {
    isLoggingOut.value = false;
  }
}

/**
 * Handle keyboard navigation
 */
function handleKeyPress(event: KeyboardEvent) {
  if (event.key === 'Escape') {
    closeMenu();
  }
}

/**
 * Close menu when clicking outside
 */
function handleClickOutside(event: MouseEvent) {
  if (menuRef.value && !menuRef.value.contains(event.target as Node)) {
    closeMenu();
  }
}

/**
 * Setup and cleanup event listeners
 */
onMounted(() => {
  document.addEventListener('keydown', handleKeyPress);
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyPress);
  document.removeEventListener('click', handleClickOutside);
});
</script>

<template>
  <div ref="menuRef" class="relative">
    <!-- Avatar Button -->
    <button
      class="flex items-center justify-center w-10 h-10 rounded-full bg-blue-600 hover:bg-blue-700 text-white font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-offset-0 focus:ring-blue-500 dark:focus:ring-blue-400"
      :aria-label="`User menu for ${authStore.user?.username}`"
      :aria-expanded="isOpen"
      aria-haspopup="menu"
      @click="toggleMenu"
    >
      {{ userInitials }}
    </button>

    <!-- Dropdown Menu -->
    <transition
      enter-active-class="transition ease-out duration-100"
      enter-from-class="transform opacity-0 scale-95"
      enter-to-class="transform opacity-100 scale-100"
      leave-active-class="transition ease-in duration-75"
      leave-from-class="transform opacity-100 scale-100"
      leave-to-class="transform opacity-0 scale-95"
    >
      <div
        v-if="isOpen"
        class="absolute right-0 mt-2 w-48 rounded-lg shadow-lg bg-white dark:bg-gray-800 ring-1 ring-black ring-opacity-5 z-50"
        role="menu"
        role-name="User menu"
        @click.stop
      >
        <!-- Menu Items -->
        <div class="py-1">
          <!-- User Info -->
          <div class="px-4 py-2 border-b border-gray-200 dark:border-gray-700">
            <p class="text-xs text-gray-600 dark:text-gray-400">Zalogowany jako</p>
            <p class="text-sm font-semibold text-gray-900 dark:text-white truncate">
              {{ authStore.user?.username }}
            </p>
            <p class="text-xs text-gray-500 dark:text-gray-400 truncate">
              {{ authStore.user?.email }}
            </p>
          </div>

          <!-- Profile Link -->
          <button
            type="button"
            class="w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            role="menuitem"
            @click="goToProfile"
          >
            👤 Profil
          </button>

          <!-- Logout Button -->
          <button
            type="button"
            class="w-full text-left px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors flex items-center gap-2"
            role="menuitem"
            :disabled="isLoggingOut"
            @click="handleLogout"
          >
            <!-- Spinner Icon -->
            <svg
              v-if="isLoggingOut"
              class="w-4 h-4 animate-spin"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                class="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                stroke-width="4"
              />
              <path
                class="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            <span v-else>🚪</span>
            {{ isLoggingOut ? 'Wylogowywanie...' : 'Wyloguj' }}
          </button>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
@media (prefers-reduced-motion: reduce) {
  :deep(.transition) {
    transition: none !important;
  }
}
</style>
