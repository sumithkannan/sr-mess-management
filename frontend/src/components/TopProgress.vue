<template>
  <div class="fixed top-0 left-0 w-full h-0.5 z-[10000] pointer-events-none">
    <div 
      class="h-full bg-blue-600 transition-all duration-300 ease-out"
      :style="{ width: progress + '%' }"
      :class="{ 'opacity-0': progress === 0 || progress === 100 }"
    ></div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const progress = ref(0)
let timer = null

router.beforeEach((to, from, next) => {
  progress.value = 0
  clearInterval(timer)
  timer = setInterval(() => {
    if (progress.value < 90) {
      progress.value += Math.random() * 10
    }
  }, 100)
  next()
})

router.afterEach(() => {
  clearInterval(timer)
  progress.value = 100
  setTimeout(() => {
    progress.value = 0
  }, 300)
})
</script>
