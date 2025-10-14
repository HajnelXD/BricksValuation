import { createRouter, createWebHistory } from 'vue-router';
import type { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  { path: '/', name: 'home', component: () => import('../components/HelloWorld.vue') },
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});
