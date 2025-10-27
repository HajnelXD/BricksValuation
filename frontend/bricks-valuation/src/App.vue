<script setup lang="ts">
import MainNavigation from '@/components/navigation/MainNavigation.vue';
import NotificationToaster from '@/components/base/NotificationToaster.vue';
</script>

<template>
  <div class="min-h-screen bg-gray-50 text-gray-900">
    <MainNavigation />
    <main>
      <RouterView />
    </main>
    <NotificationToaster />
  </div>
</template>

<style scoped>
main {
  min-height: calc(100vh - 4rem);
}
</style>
