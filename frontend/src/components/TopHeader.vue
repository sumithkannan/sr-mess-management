<template>
  <header class="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between max-w-lg mx-auto w-full">
    <h1 class="font-bold text-lg text-gray-800">Mess Manager</h1>
    <div class="flex items-center gap-3">
      <span class="text-sm text-gray-600">{{ auth.user?.name }}</span>
      <button @click="auth.logout(); $router.push('/login')" class="text-sm text-red-500">Logout</button>
    </div>
  </header>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'
const auth = useAuthStore()
</script>
