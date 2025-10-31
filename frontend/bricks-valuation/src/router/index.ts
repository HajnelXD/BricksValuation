import { createRouter, createWebHistory } from 'vue-router';
import type { RouteRecordRaw } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

declare module 'vue-router' {
  interface RouteMeta {
    requiresGuest?: boolean;
    requiresAuth?: boolean;
  }
}

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'public-bricksets',
    component: () => import('../pages/bricksets/LandingBrickSetListView.vue'),
  },
  {
    path: '/bricksets/:id',
    name: 'brickset-detail',
    component: () => import('../pages/bricksets/PublicBrickSetDetailView.vue'),
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../pages/auth/LoginView.vue'),
    meta: { requiresGuest: true },
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('../pages/auth/RegisterView.vue'),
    meta: { requiresGuest: true },
  },
  {
    path: '/app/bricksets/new',
    name: 'brickset-create',
    component: () => import('../pages/bricksets/BrickSetCreateView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/app/bricksets/:id/edit',
    name: 'brickset-edit',
    component: () => import('../pages/bricksets/BrickSetEditView.vue'),
    meta: { requiresAuth: true },
  },
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});

/**
 * Global route guard for authentication checks
 * Handles:
 * - Session validation on app initialization
 * - Protection of guest-only routes (requiresGuest)
 * - Protection of authenticated routes (requiresAuth)
 * - Deep linking with redirect parameter
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
router.beforeEach(async (to: any, _from: any, next: any) => {
  const authStore = useAuthStore();

  // Initialize session on first route (only if user is null and not already loading)
  // This checks if the user has a valid JWT cookie session
  if (authStore.user === null && !authStore.isLoading) {
    await authStore.fetchProfile();
  }

  // Guard: requiresGuest (login, register pages)
  // Redirect authenticated users away from guest-only pages
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next({ name: 'public-bricksets' });
    return;
  }

  // Guard: requiresAuth (protected app routes)
  // Redirect unauthenticated users to login with redirect parameter
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({
      name: 'login',
      query: { redirect: to.fullPath },
    });
    return;
  }

  // Allow navigation
  next();
});
