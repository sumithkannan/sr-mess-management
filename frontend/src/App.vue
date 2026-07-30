<template>
  <div class="min-h-screen bg-gray-50">
    <TopHeader v-if="auth.isAuthenticated" />
    <main class="pb-20 px-4 pt-4 max-w-lg mx-auto w-full">
      <router-view :key="$route.fullPath" />
    </main>
    <BottomNav v-if="auth.isAuthenticated" />
  </div>
</template>

<script setup>
import { useAuthStore } from './stores/auth'
import TopHeader from './components/TopHeader.vue'
import BottomNav from './components/BottomNav.vue'
const auth = useAuthStore()
</script>
