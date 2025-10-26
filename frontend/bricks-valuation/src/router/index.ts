import { createRouter, createWebHistory } from 'vue-router';
import type { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'public-bricksets',
    component: () => import('../pages/bricksets/LandingBrickSetListView.vue'),
  },
  {
    path: '/bricksets',
    redirect: '/',
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
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});
