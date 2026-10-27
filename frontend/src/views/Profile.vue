<template>
  <div class="space-y-4">
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
    </div>

    <div class="bg-white rounded-lg border p-6 space-y-3">
      <button @click="showChangePassword = !showChangePassword" class="flex items-center justify-between w-full text-left">
        <h2 class="font-semibold text-lg">Security</h2>
        <span class="text-blue-600 text-sm">{{ showChangePassword ? 'Cancel' : 'Change Password' }}</span>
      </button>
      <div v-if="showChangePassword" class="pt-2 border-t space-y-3">
        <form @submit.prevent="changePassword" class="space-y-3">
          <div>
            <label class="block text-sm text-gray-700 mb-1">Current Password</label>
            <input v-model="form.current_password" type="password" required class="w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div>
            <label class="block text-sm text-gray-700 mb-1">New Password</label>
            <input v-model="form.new_password" type="password" required minlength="6" class="w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
            <p class="text-xs text-gray-500 mt-1">Minimum 6 characters</p>
          </div>
          <div>
            <label class="block text-sm text-gray-700 mb-1">Confirm New Password</label>
            <input v-model="form.confirm_password" type="password" required minlength="6" class="w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <button type="submit" class="w-full bg-blue-600 text-white py-2.5 rounded text-sm hover:bg-blue-700">
            Update Password
          </button>
        </form>
      </div>
    </div>

    <VersionTag />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useToast } from '../composables/useToast'
import api from '../api'
import VersionTag from '../components/VersionTag.vue'

const auth = useAuthStore()
const toast = useToast()

const form = ref({
  current_password: '',
  new_password: '',
  confirm_password: ''
})
const showChangePassword = ref(false)

async function changePassword() {
  if (form.value.new_password !== form.value.confirm_password) {
    toast.error('New passwords do not match')
    return
  }
  if (form.value.new_password.length < 6) {
    toast.error('New password must be at least 6 characters')
    return
  }
  try {
    await api.post('/api/auth/change-password', {
      current_password: form.value.current_password,
      new_password: form.value.new_password
    })
    toast.success('Password changed successfully')
    form.value = {
      current_password: '',
      new_password: '',
      confirm_password: ''
    }
    showChangePassword.value = false
  } catch (e) {
    toast.error(e.response?.data?.detail || 'Failed to change password')
  }
}
</script>
