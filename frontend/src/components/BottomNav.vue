<template>
  <nav class="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-50">
    <div class="flex justify-around items-center h-14 max-w-lg mx-auto">
      <router-link v-for="tab in tabs" :key="tab.path" :to="tab.path"
        class="flex flex-col items-center justify-center px-3 py-1 text-xs"
        :class="$route.path.startsWith(tab.path) ? 'text-blue-600' : 'text-gray-500'">
        <span class="text-lg leading-none" v-html="tab.icon"></span>
        <span class="mt-0.5">{{ tab.label }}</span>
      </router-link>
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '../stores/auth'
const auth = useAuthStore()
const tabs = computed(() => {
  const items = [
    { path: '/dashboard', label: 'Home', icon: '&#8962;' },
    { path: '/menu', label: 'Menu', icon: '&#9776;' },
  ]
  items.push({ path: '/attendance', label: 'Attendance', icon: '&#10003;' })
  if (auth.isAdmin) {
    items.push({ path: '/reports', label: 'Reports', icon: '&#128202;' })
  }
  items.push({ path: '/profile', label: 'More', icon: '&#8942;' })
  return items
})
</script>
