<script setup lang="ts">
import { RouterView, RouterLink } from 'vue-router';
</script>

<template>
  <div id="app" class="min-h-screen bg-gray-50 flex flex-col">
    
    <header class="bg-white shadow-md sticky top-0 z-10">
      <div class="container mx-auto px-4 py-4 flex justify-between items-center">
        <RouterLink to="/" class="text-2xl font-extrabold text-blue-700 hover:text-blue-900 transition duration-150">
          TankIQ ⛽
        </RouterLink>

        <nav class="space-x-4">
          <RouterLink 
            to="/" 
            class="text-gray-600 hover:text-blue-600 font-medium transition duration-150" 
            active-class="text-blue-600 border-b-2 border-blue-600 pb-1"
          >
            Log
          </RouterLink>
          <RouterLink 
            to="/stats" 
            class="text-gray-600 hover:text-blue-600 font-medium transition duration-150"
            active-class="text-blue-600 border-b-2 border-blue-600 pb-1"
          >
            Stats
          </RouterLink>
          <RouterLink 
            to="/entry/add" 
            class="ml-4 px-3 py-1 bg-green-500 text-white rounded-md hover:bg-green-600 transition duration-150 shadow-sm"
          >
            + Add
          </RouterLink>
        </nav>
      </div>
    </header>

    <main class="flex-grow pb-10">
      <RouterView />
    </main>
    
    <footer class="bg-gray-200 text-gray-600 text-center text-sm p-4">
      TankIQ - Fuel Log Analyzer
    </footer>
  </div>
</template>

<style>
/* Global Styles (not scoped) */
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
}
</style>