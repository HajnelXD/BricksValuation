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
    name: 'app-bricksets' as const,
    label: t('nav.appSets'),
    icon: '🗂',
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
    class="fixed top-0 left-0 right-0 bg-white border-b border-gray-200 shadow-sm z-50"
  >
    <div class="mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex h-20 gap-8">
        <!-- Navigation Tiles -->
        <div class="flex items-start gap-8">
          <template v-for="link in visibleNavigationLinks" :key="link.name">
            <!-- Logout Button (Action Button) -->
            <a
              v-if="link.isAction"
              class="px-4 py-2 transition-all duration-200 text-sm font-medium whitespace-nowrap bg-blue-100 text-blue-700 border border-blue-300 cursor-pointer"
              @click="handleLogout"
            >
              <span class="mr-2">{{ link.icon }}</span
              >{{ link.label }}
            </a>
            <!-- Regular Navigation Link -->
            <RouterLink
              v-else
              :to="{ name: link.name }"
              class="px-4 py-2 transition-all duration-200 text-sm font-medium whitespace-nowrap"
              :class="
                isActive(link.name)
                  ? 'bg-blue-100 text-blue-700 border border-blue-300'
                  : 'text-gray-700 hover:bg-gray-100 border border-transparent hover:border-gray-300'
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
  <div v-if="isAuthenticated" class="h-20"></div>
</template>

<style scoped>
nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 50;
}
</style>
