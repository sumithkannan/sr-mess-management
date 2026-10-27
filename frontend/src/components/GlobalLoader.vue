<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="loadingStore.loading" class="fixed inset-0 z-[9999] flex items-center justify-center bg-black/40 backdrop-blur-sm">
        <div class="flex flex-col items-center gap-3 rounded-2xl bg-white px-6 py-5 shadow-2xl">
          <div class="relative h-10 w-10">
            <div class="absolute inset-0 rounded-full border-4 border-gray-200"></div>
            <div class="absolute inset-0 animate-spin rounded-full border-4 border-transparent border-t-blue-600"></div>
          </div>
          <p class="text-sm font-medium text-gray-700">Please wait...</p>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { useLoadingStore } from '../stores/loading'

const loadingStore = useLoadingStore()
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
