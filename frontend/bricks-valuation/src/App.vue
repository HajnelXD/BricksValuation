<script setup lang="ts">
import MainNavigation from '@/components/navigation/MainNavigation.vue';
import NotificationToaster from '@/components/base/NotificationToaster.vue';
</script>

<template>
  <div class="flex flex-col min-h-screen bg-gray-900 text-gray-100">
    <MainNavigation />
    <main class="flex-1">
      <RouterView />
    </main>
    <NotificationToaster />
  </div>
</template>

<style scoped>
main {
  min-height: calc(100vh - 5rem);
}
</style>
