<template>
  <div class="bg-white rounded-lg border p-6 space-y-4">
    <h2 class="font-semibold text-lg">Profile</h2>
    <div class="space-y-2 text-sm">
      <p><span class="text-gray-500">Username:</span> {{ auth.user?.username }}</p>
      <p><span class="text-gray-500">Name:</span> {{ auth.user?.name }}</p>
      <p><span class="text-gray-500">Email:</span> {{ auth.user?.email || '-' }}</p>
      <p><span class="text-gray-500">Role:</span>
        <span class="px-2 py-0.5 rounded text-xs" :class="auth.isAdmin ? 'bg-purple-100 text-purple-700' : 'bg-blue-100 text-blue-700'">
          {{ auth.user?.role }}
        </span>
      </p>
    </div>

    <div class="pt-4 border-t">
      <h3 class="font-medium text-sm mb-2">Quick Links</h3>
      <div class="space-y-1">
        <router-link v-if="auth.isAdmin" to="/users" class="block text-blue-600 text-sm py-1">User Management</router-link>
        <router-link v-if="auth.isAdmin" to="/expenses" class="block text-blue-600 text-sm py-1">Expenses</router-link>
        <router-link v-if="auth.isAdmin" to="/admin" class="block text-blue-600 text-sm py-1">Settings</router-link>
        <router-link to="/ratings" class="block text-blue-600 text-sm py-1">Rate Meals</router-link>
        <router-link to="/menu" class="block text-blue-600 text-sm py-1">View Menu</router-link>
      </div>
    </div>

    <button @click="auth.logout(); $router.push('/login')"
      class="w-full bg-red-500 text-white py-2.5 rounded text-sm hover:bg-red-600 mt-2">
      Logout
    </button>

    <VersionTag />
  </div>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'
import VersionTag from '../components/VersionTag.vue'
const auth = useAuthStore()
</script>
