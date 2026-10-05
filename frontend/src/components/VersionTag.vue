<template>
  <p class="text-[11px] text-center text-gray-400 mt-3 font-mono">
    <template v-if="info">
      api {{ info.commit || 'dev' }}
      <span v-if="info.branch">· {{ info.branch }}</span>
      <span v-if="info.deployed_at">· {{ info.deployed_at }}</span>
    </template>
    <template v-else-if="failed">api unreachable</template>
    <template v-else>checking api…</template>
  </p>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import api from '../api'

const info = ref(null)
const failed = ref(false)

onMounted(async () => {
  try {
    const { data } = await api.get('/version')
    info.value = data
  } catch {
    failed.value = true
  }
})
</script>