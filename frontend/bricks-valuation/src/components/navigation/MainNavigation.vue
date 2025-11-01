<script setup lang="ts">
/**
 * MainNavigation Component
 * Top-level navigation bar that adapts to authentication state
 */
import { computed, ref } from 'vue';
import { useRoute, RouterLink, useRouter } from 'vue-router';
import { storeToRefs } from 'pinia';
import { useI18n } from 'vue-i18n';
import { useAuthStore } from '@/stores/auth';
import { useNotificationStore } from '@/stores/notification';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const notificationStore = useNotificationStore();
const { isAuthenticated } = storeToRefs(authStore);
const { t } = useI18n();

const isLoggingOut = ref(false);

const navTiles = computed(() => [
  {
    name: 'public-bricksets' as const,
    label: t('nav.publicSets'),
    icon: '📦',
    requiresAuth: false,
    isAction: false,
  },
  {
    name: 'my-bricksets' as const,
    label: t('nav.mySets'),
    icon: '🏠',
    requiresAuth: true,
    isAction: false,
  },
  {
    name: 'brickset-create' as const,
    label: t('bricksets.create.addNew'),
    icon: '➕',
    requiresAuth: true,
    isAction: false,
  },
  {
    name: 'my-valuations' as const,
    label: t('nav.myValuations'),
    icon: '⭐',
    requiresAuth: true,
    isAction: false,
  },
  {
    name: 'logout' as const,
    label: t('nav.logout'),
    icon: '🚪',
    requiresAuth: true,
    isAction: true,
  },
]);

const visibleNavigationLinks = computed(() => {
  return navTiles.value.filter((tile) => {
    if (tile.requiresAuth) {
      return isAuthenticated.value;
    }
    return true;
  });
});

function isActive(name: string): boolean {
  return route.name === name;
}

async function handleLogout() {
  isLoggingOut.value = true;

  try {
    await authStore.logout();

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
</script>

<template>
  <nav
    v-if="isAuthenticated"
    class="fixed top-0 left-0 right-0 bg-gray-900 border-b border-gray-800 shadow-lg z-50"
  >
    <div class="mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex h-16 items-center gap-4">
        <!-- Navigation Links -->
        <div class="flex items-center gap-2">
          <template v-for="link in visibleNavigationLinks" :key="link.name">
            <!-- Logout Button (Action Button) -->
            <button
              v-if="link.isAction"
              type="button"
              class="px-3 py-2 rounded-md transition-all duration-200 text-sm font-medium whitespace-nowrap bg-gray-800 text-gray-300 hover:bg-gray-700 hover:text-white border border-gray-700 hover:border-gray-600 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
              :disabled="isLoggingOut"
              @click="handleLogout"
            >
              <span class="mr-2">{{ link.icon }}</span
              >{{ link.label }}
            </button>
            <!-- Regular Navigation Link -->
            <RouterLink
              v-else
              :to="{ name: link.name }"
              class="px-3 py-2 rounded-md transition-all duration-200 text-sm font-medium whitespace-nowrap border"
              :class="
                isActive(link.name)
                  ? 'bg-gray-800 text-white border-gray-600'
                  : 'text-gray-400 hover:bg-gray-800 hover:text-gray-200 border-transparent hover:border-gray-700'
              "
            >
              <span class="mr-2">{{ link.icon }}</span
              >{{ link.label }}
            </RouterLink>
          </template>
        </div>
      </div>
    </div>
  </nav>
  <!-- Spacer to prevent content from hiding under fixed nav -->
  <div v-if="isAuthenticated" class="h-16"></div>
</template>
