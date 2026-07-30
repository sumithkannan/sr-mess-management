<template>
  <div class="space-y-4">
    <h2 class="font-semibold">Rate Your Meals</h2>
    <input type="date" v-model="selectedDate" class="w-full border rounded px-3 py-2 text-sm" />

    <div v-for="mt in mealTypes" :key="mt.id" class="bg-white rounded-xl border overflow-hidden">
      <div class="px-4 py-3 border-b border-gray-100">
        <h3 class="font-medium text-gray-900">{{ mt.name }}</h3>
        <p v-if="mt.start_time" class="text-xs text-gray-500">{{ mt.start_time.substring(0,5) }} – {{ mt.end_time?.substring(0,5) }}</p>
      </div>

      <div v-for="item in getItems(mt.id)" :key="item.id" class="px-4 py-3 border-b border-gray-50 last:border-0">
        <div class="flex items-center justify-between">
          <span class="text-sm font-medium text-gray-800">{{ item.item_name }}</span>
          <div class="flex items-center gap-1"
            :class="canRate(mt) ? '' : 'pointer-events-none'"
            @mouseleave="onStarLeave(item.id)">
            <span v-for="s in 5" :key="s"
              @click="rate(mt, item.id, s)"
              @mouseenter="onStarEnter(item.id, s)"
              class="text-xl transition-colors duration-100 select-none"
              :class="starClass(item.id, s)">
              ★
            </span>
          </div>
        </div>
        <p v-if="!isRatingOpen(mt)" class="text-xs mt-1 text-right text-gray-400">Rating not yet open</p>
        <p v-else-if="!hasVoted(mt.id)" class="text-xs mt-1 text-right text-gray-400">Vote first to rate</p>
        <p v-else-if="myRatings[item.id]" class="text-xs mt-1 text-right text-yellow-600">
          Tap to update — {{ '★'.repeat(myRatings[item.id]) }}{{ '☆'.repeat(5 - myRatings[item.id]) }}
        </p>
      </div>

      <div v-if="getItems(mt.id).length === 0" class="px-4 py-3 text-sm text-gray-400">No items</div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import api from '../api'

const selectedDate = ref(new Date().toISOString().split('T')[0])
const mealTypes = ref([])
const menuItems = ref([])
const myRatings = ref({})
const hoverRating = reactive({})
const votes = ref([])

async function load() {
  try {
    const [mt, mi, r, v] = await Promise.all([
      api.get('/api/meal-types'),
      api.get(`/api/menu-items/date/${selectedDate.value}`),
      api.get(`/api/ratings/my/${selectedDate.value}`),
      api.get(`/api/votes/my/${selectedDate.value}`)
    ])
    votes.value = v.data
    mealTypes.value = mt.data.filter(m => m.is_active)
    menuItems.value = mi.data
    myRatings.value = {}
    for (const rr of r.data) {
      myRatings.value[rr.menu_item_id] = rr.rating
    }
  } catch (e) {
    console.error('Ratings load error:', e)
  }
}

function getItems(mtId) { return menuItems.value.filter(i => i.meal_type_id === mtId) }

function getRatingStart(mt) {
  if (!mt.end_time || mt.rating_start_hours == null) return null
  const d = new Date(selectedDate.value + 'T00:00:00')
  const [h, m] = mt.end_time.split(':')
  d.setHours(+h, +m, 0, 0)
  return new Date(d.getTime() + mt.rating_start_hours * 3600000)
}

function isRatingOpen(mt) {
  const start = getRatingStart(mt)
  if (!start) return false
  return new Date() >= start
}

function hasVoted(mtId) {
  return votes.value.some(v => v.meal_type_id === mtId)
}

function canRate(mt) {
  return isRatingOpen(mt) && hasVoted(mt.id)
}

function starClass(itemId, s) {
  const effective = hoverRating[itemId] || myRatings.value[itemId] || 0
  return s <= effective ? 'text-yellow-400' : 'text-gray-300'
}

function onStarEnter(itemId, s) {
  hoverRating[itemId] = s
}

function onStarLeave(itemId) {
  hoverRating[itemId] = 0
}

async function rate(mt, itemId, rating) {
  if (!itemId || !canRate(mt)) return
  try {
    await api.post('/api/ratings', { menu_item_id: itemId, meal_type_id: mt.id, date: selectedDate.value, rating })
    myRatings.value[itemId] = rating
    hoverRating[itemId] = 0
  } catch (e) { alert(e.response?.data?.detail || 'Error') }
}

watch(selectedDate, load)
onMounted(load)
</script>
