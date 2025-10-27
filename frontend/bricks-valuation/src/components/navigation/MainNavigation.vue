<script setup lang="ts">
/**
 * MainNavigation Component
 * Top-level navigation bar that adapts to authentication state
 */
import { computed } from 'vue';
import { useRoute, RouterLink } from 'vue-router';
import { storeToRefs } from 'pinia';
import { useI18n } from 'vue-i18n';
import { useAuthStore } from '@/stores/auth';
import UserMenu from '@/components/navigation/UserMenu.vue';

const route = useRoute();
const authStore = useAuthStore();
const { isAuthenticated } = storeToRefs(authStore);
const { t } = useI18n();

const brandLabel = computed(() => t('app.title'));

const navTiles = computed(() => [
  {
    name: 'public-bricksets' as const,
    label: 'Wszystkie zestawy',
    icon: '📦',
    requiresAuth: false,
  },
  {
    name: 'app-bricksets' as const,
    label: 'Moje zestawy',
    icon: '🗂',
    requiresAuth: true,
  },
]);

function isActive(name: string): boolean {
  return route.name === name;
}
</script>

<template>
  <nav v-if="isAuthenticated" class="bg-white border-b border-gray-200 shadow-sm">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex h-16 items-center justify-between">
        <!-- Brand -->
        <RouterLink
          to="/"
          class="text-lg font-semibold text-blue-600 hover:text-blue-700 transition-colors"
        >
          {{ brandLabel }}
        </RouterLink>

        <!-- Links -->
        <div class="flex items-center gap-6">
          <div class="hidden md:flex items-center gap-4">
            <RouterLink
              v-for="link in visibleNavigationLinks"
              :key="link.name"
              :to="{ name: link.name }"
              class="text-sm font-medium transition-colors"
              :class="isActive(link.name) ? 'text-blue-600' : 'text-gray-600 hover:text-gray-900'"
            >
              {{ link.label }}
            </RouterLink>
          </div>

          <RouterLink
            :to="{ name: 'app-bricksets' }"
            class="md:hidden text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors"
            :class="isActive('app-bricksets') ? 'text-blue-600' : ''"
          >
            {{ t('nav.mySets') }}
          </RouterLink>

          <!-- Auth Actions -->
          <div class="flex items-center gap-3">
            <UserMenu />
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<style scoped>
@media (max-width: 768px) {
  nav {
    position: sticky;
    top: 0;
    z-index: 40;
  }
}
</style>
