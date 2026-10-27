<template>
  <Teleport to="body">
    <div class="fixed top-4 left-1/2 -translate-x-1/2 z-[9999] space-y-2 w-full max-w-sm px-4">
      <TransitionGroup name="toast">
        <div v-for="t in toasts" :key="t.id"
          class="px-4 py-3 rounded-lg shadow-lg text-sm font-medium flex items-center justify-between"
          :class="{
            'bg-green-50 text-green-700 border border-green-200': t.type === 'success',
            'bg-yellow-50 text-yellow-700 border border-yellow-200': t.type === 'warning',
            'bg-red-50 text-red-700 border border-red-200': t.type === 'error',
            'bg-blue-50 text-blue-700 border border-blue-200': t.type === 'info'
          }">
          <span>{{ t.message }}</span>
          <button @click="remove(t.id)" class="ml-3 opacity-70 hover:opacity-100">×</button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup>
import { useToast } from '../composables/useToast'
const { toasts, remove } = useToast()
</script>

<style scoped>
.toast-enter-active, .toast-leave-active { transition: all 0.3s ease; }
.toast-enter-from { opacity: 0; transform: translateY(-20px); }
.toast-leave-to { opacity: 0; transform: translateY(-20px); }
</style>
