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
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});
