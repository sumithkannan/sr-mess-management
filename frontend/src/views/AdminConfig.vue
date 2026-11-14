<template>
  <div class="space-y-6">
    <h2 class="font-semibold">Meal Types</h2>

    <button @click="showForm = !showForm"
      class="bg-blue-600 text-white px-4 py-2 rounded text-sm w-full">
      {{ showForm ? 'Cancel' : '+ Add Meal Type' }}
    </button>

    <div v-if="showForm" class="bg-white border rounded-lg p-4 space-y-3">
      <input v-model="form.name" placeholder="Name (e.g. Breakfast)"
        class="w-full border rounded px-3 py-2 text-sm" />
      <label class="flex items-center gap-2 text-sm">
        <span class="w-28">Start time:</span>
        <input type="time" v-model="form.start_time" class="border rounded px-2 py-1 text-sm flex-1" />
      </label>
      <label class="flex items-center gap-2 text-sm">
        <span class="w-28">End time:</span>
        <input type="time" v-model="form.end_time" class="border rounded px-2 py-1 text-sm flex-1" />
      </label>
      <label class="flex items-center gap-2 text-sm">
        <span class="w-28 shrink-0">Vote cutoff (hrs):</span>
        <input type="number" v-model.number="form.vote_cutoff_hours" min="1" max="72"
          class="border rounded px-2 py-1 text-sm w-20" />
        <span class="text-xs text-gray-500">{{ voteCutoffHint(form) }}</span>
      </label>
      <label class="flex items-center gap-2 text-sm">
        <span class="w-28 shrink-0">Vote open (days):</span>
        <input type="number" v-model.number="form.vote_open_interval_days" min="1" max="90"
          class="border rounded px-2 py-1 text-sm flex-1" />
      </label>
      <label class="flex items-center gap-2 text-sm">
        <span class="w-28 shrink-0">Rating after (hrs):</span>
        <input type="number" v-model.number="form.rating_start_hours" min="0" max="72"
          class="border rounded px-2 py-1 text-sm w-20" />
        <span class="text-xs text-gray-500">{{ ratingHint(form) }}</span>
      </label>
      <label class="flex items-center gap-2 text-sm">
        <span class="w-28 shrink-0">Attendance buf (hrs):</span>
        <input type="number" v-model.number="form.attendance_buffer_hours" min="0" max="24"
          class="border rounded px-2 py-1 text-sm w-20" />
        <span class="text-xs text-gray-500">{{ attendanceHint(form) }}</span>
      </label>
      <label class="flex items-center gap-2 text-sm">
        <span class="w-28">Sort order:</span>
        <input type="number" v-model.number="form.sort_order" class="border rounded px-2 py-1 text-sm w-20" />
      </label>
      <button @click="addMealType" class="bg-green-600 text-white px-4 py-1.5 rounded text-sm">Create</button>
    </div>

    <div v-for="mt in mealTypes" :key="mt.id" class="bg-white border rounded-lg p-4 space-y-3">
      <div class="flex justify-between items-center">
        <h3 class="font-medium text-base">{{ mt.name }}</h3>
        <button @click="deleteMealType(mt.id)" class="text-red-500 text-xs hover:text-red-700">Delete</button>
      </div>
      <div class="space-y-2 text-sm">
        <label class="flex items-center gap-2">
          <span class="w-28">Start time:</span>
          <input type="time" v-model="mt.start_time" class="border rounded px-2 py-1 text-sm flex-1" />
        </label>
        <label class="flex items-center gap-2">
          <span class="w-28">End time:</span>
          <input type="time" v-model="mt.end_time" class="border rounded px-2 py-1 text-sm flex-1" />
        </label>
        <label class="flex items-center gap-2">
          <span class="w-28 shrink-0">Vote cutoff (hrs):</span>
          <input type="number" v-model.number="mt.vote_cutoff_hours" min="1" max="72"
            class="border rounded px-2 py-1 text-sm w-20" />
          <span class="text-xs text-gray-500">{{ voteCutoffHint(mt) }}</span>
        </label>
        <label class="flex items-center gap-2">
          <span class="w-28 shrink-0">Vote open (days):</span>
          <input type="number" v-model.number="mt.vote_open_interval_days" min="1" max="90"
            class="border rounded px-2 py-1 text-sm flex-1" />
        </label>
        <label class="flex items-center gap-2">
          <span class="w-28 shrink-0">Rating after (hrs):</span>
          <input type="number" v-model.number="mt.rating_start_hours" min="0" max="72"
            class="border rounded px-2 py-1 text-sm w-20" />
          <span class="text-xs text-gray-500">{{ ratingHint(mt) }}</span>
        </label>
        <label class="flex items-center gap-2">
          <span class="w-28 shrink-0">Attendance buf (hrs):</span>
          <input type="number" v-model.number="mt.attendance_buffer_hours" min="0" max="24"
            class="border rounded px-2 py-1 text-sm w-20" />
          <span class="text-xs text-gray-500">{{ attendanceHint(mt) }}</span>
        </label>
      </div>
      <button @click="updateMealType(mt)" class="bg-blue-600 text-white px-4 py-1.5 rounded text-sm">Save</button>
    </div>

    <div v-if="mealTypes.length === 0" class="text-center py-8 text-gray-400 text-sm">
      No meal types yet. Add one above.
    </div>

    <hr class="my-4" />

    <h2 class="font-semibold">Off Days</h2>

    <button @click="showOffForm = !showOffForm"
      class="bg-blue-600 text-white px-4 py-2 rounded text-sm w-full">
      {{ showOffForm ? 'Cancel' : '+ Mark Off Day' }}
    </button>

    <div v-if="showOffForm" class="bg-white border rounded-lg p-4 space-y-3">
      <label class="flex items-center gap-2 text-sm">
        <span class="w-16">From:</span>
        <input type="date" v-model="offForm.start_date" class="border rounded px-2 py-1 text-sm flex-1" />
      </label>
      <label class="flex items-center gap-2 text-sm">
        <span class="w-16">To:</span>
        <input type="date" v-model="offForm.end_date" class="border rounded px-2 py-1 text-sm flex-1" />
      </label>
      <input v-model="offForm.reason" placeholder="Reason (optional)"
        class="w-full border rounded px-3 py-2 text-sm" />
      <button @click="addOffDay" class="bg-green-600 text-white px-4 py-1.5 rounded text-sm">Create</button>
    </div>

    <div v-for="o in offDays" :key="o.id" class="bg-white border rounded-lg p-4 flex justify-between items-center">
      <div class="text-sm">
        <span class="font-medium">{{ o.start_date }}</span>
        <span v-if="o.start_date !== o.end_date"> – {{ o.end_date }}</span>
        <span v-if="o.reason" class="text-gray-500"> — {{ o.reason }}</span>
      </div>
      <button @click="deleteOffDay(o.id)" class="text-red-500 text-xs hover:text-red-700">Delete</button>
    </div>

    <div v-if="offDays.length === 0" class="text-center py-4 text-gray-400 text-sm">
      No off days set.
    </div>
  </div>
</template>

<script setup>
const toast = useToast()
import { ref, onMounted } from 'vue'
import api from '../api'
import { useToast } from '../composables/useToast'
import { clockMinutes, describeClockOffset } from '../utils/time'

const mealTypes = ref([])
const showForm = ref(false)
const form = ref({ name: '', start_time: '', end_time: '', vote_cutoff_hours: 12, vote_open_interval_days: 7, rating_start_hours: 2, attendance_buffer_hours: 1, sort_order: 0 })
const offDays = ref([])
const showOffForm = ref(false)
const offForm = ref({ start_date: '', end_date: '', reason: '' })

function normalizeTime(mealTypes) {
  for (const mt of mealTypes) {
    mt.start_time = mt.start_time?.substring(0, 5)
    mt.end_time = mt.end_time?.substring(0, 5)
  }
}

const DAY_MINUTES = 24 * 60

function hoursValue(value) {
  if (value === '' || value === null || value === undefined) return null
  const hours = Number(value)
  return Number.isFinite(hours) ? hours : null
}

// Votes close this long before the meal starts, e.g. 09:00 with 14 hrs
// closes at 7:00 PM the previous day.
function voteCutoffHint(mt) {
  const start = clockMinutes(mt.start_time)
  const hours = hoursValue(mt.vote_cutoff_hours)
  if (start == null || hours == null) return ''
  return `→ ${describeClockOffset(start - hours * 60)}`
}

// Ratings open this long after the meal ends.
function ratingHint(mt) {
  const end = clockMinutes(mt.end_time)
  const hours = hoursValue(mt.rating_start_hours)
  if (end == null || hours == null) return ''
  return `→ ${describeClockOffset(end + hours * 60)}`
}

// Attendance is accepted from `buffer` before the start until `buffer` after
// the end (the backend also rolls a meal that crosses midnight to the next day).
function attendanceHint(mt) {
  const start = clockMinutes(mt.start_time)
  const end = clockMinutes(mt.end_time)
  const hours = hoursValue(mt.attendance_buffer_hours) ?? 1
  if (start == null || end == null) return ''
  const open = start - hours * 60
  let close = end + hours * 60
  if (close <= open) close += DAY_MINUTES
  return `→ ${describeClockOffset(open)} – ${describeClockOffset(close)}`
}

async function load() {
  try {
    const [mtRes, offRes] = await Promise.all([
      api.get('/api/meal-types'),
      api.get('/api/off-days')
    ])
    normalizeTime(mtRes.data)
    mealTypes.value = mtRes.data
    offDays.value = offRes.data
  } catch (e) {
    console.error('AdminConfig load error:', e)
  }
}

async function addMealType() {
  try {
    const payload = {
      name: form.value.name,
      start_time: form.value.start_time,
      end_time: form.value.end_time,
      vote_cutoff_hours: form.value.vote_cutoff_hours || 12,
      vote_open_interval_days: form.value.vote_open_interval_days || 7,
      rating_start_hours: form.value.rating_start_hours || 2,
      attendance_buffer_hours: form.value.attendance_buffer_hours || 1,
      sort_order: form.value.sort_order || 0
    }
    const { data } = await api.post('/api/meal-types', payload)
    data.start_time = data.start_time?.substring(0, 5)
    data.end_time = data.end_time?.substring(0, 5)
    mealTypes.value.push(data)
    form.value = { name: '', start_time: '', end_time: '', vote_cutoff_hours: 12, vote_open_interval_days: 7, rating_start_hours: 2, attendance_buffer_hours: 1, sort_order: 0 }
    showForm.value = false
  } catch (e) { toast.error('Error: ' + (e.response?.data?.detail || e.message)) }
}

async function updateMealType(mt) {
  try {
    await api.put(`/api/meal-types/${mt.id}`, {
      start_time: mt.start_time,
      end_time: mt.end_time,
      vote_cutoff_hours: mt.vote_cutoff_hours,
      vote_open_interval_days: mt.vote_open_interval_days,
      rating_start_hours: mt.rating_start_hours,
      attendance_buffer_hours: mt.attendance_buffer_hours
    })
    toast.success('Updated')
  } catch (e) { toast.error('Error: ' + (e.response?.data?.detail || e.message)) }
}

async function deleteMealType(id) {
  if (!confirm('Delete this meal type?')) return
  try {
    await api.delete(`/api/meal-types/${id}`)
    mealTypes.value = mealTypes.value.filter(m => m.id !== id)
  } catch (e) { toast.error('Error: ' + (e.response?.data?.detail || e.message)) }
}

async function addOffDay() {
  try {
    const payload = {
      start_date: offForm.value.start_date,
      end_date: offForm.value.end_date || offForm.value.start_date,
      reason: offForm.value.reason || null
    }
    const { data } = await api.post('/api/off-days', payload)
    offDays.value.push(data)
    offForm.value = { start_date: '', end_date: '', reason: '' }
    showOffForm.value = false
  } catch (e) { toast.error('Error: ' + (e.response?.data?.detail || e.message)) }
}

async function deleteOffDay(id) {
  if (!confirm('Remove this off day?')) return
  try {
    await api.delete(`/api/off-days/${id}`)
    offDays.value = offDays.value.filter(o => o.id !== id)
  } catch (e) { toast.error('Error: ' + (e.response?.data?.detail || e.message)) }
}

onMounted(load)
</script>
