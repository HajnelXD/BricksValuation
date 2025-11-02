<template>
  <div class="text-center py-16">
    <div class="text-6xl mb-4">📝</div>
    <h3 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">
      Nie dodałeś jeszcze żadnych wycen
    </h3>
    <p class="text-gray-600 dark:text-gray-400 mb-8">Przeglądaj zestawy i dodawaj swoje wyceny</p>
    <router-link
      to="/bricksets"
      class="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors dark:bg-blue-700 dark:hover:bg-blue-600"
    >
      Przejdź do zestawów
    </router-link>
  </div>
</template>

<script setup lang="ts"></script>

<style scoped></style>
