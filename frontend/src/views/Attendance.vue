<template>
  <div class="space-y-4">
    <h2 class="font-semibold">Attendance</h2>

    <div class="flex gap-2">
      <input type="date" v-model="attDate" class="border rounded px-3 py-2 text-sm flex-1" />
      <select v-model="selectedMealType" class="border rounded px-3 py-2 text-sm">
        <option value="">Select meal</option>
        <option v-for="mt in mealTypes" :key="mt.id" :value="mt.id">{{ mt.name }}</option>
      </select>
      <button @click="downloadCSV" :disabled="!selectedMealType"
        class="bg-gray-100 hover:bg-gray-200 disabled:opacity-40 px-3 py-2 rounded text-sm font-medium">
        &#8595;
      </button>
    </div>

    <template v-if="selectedMealType">
      <div class="flex items-center justify-between">
        <span class="text-xs px-2.5 py-1 rounded-full font-medium"
          :class="isAttendanceOpen ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'">
          {{ isAttendanceOpen ? 'Attendance Open' : 'Attendance Closed' }}
        </span>
        <span v-if="selectedMealTypeObj && !isAttendanceOpen" class="text-xs text-gray-400">
          Opens {{ attendanceWindowStart }}
        </span>
      </div>

      <div class="flex gap-2">
        <div class="relative flex-1">
          <span class="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-400 text-xs">&#128269;</span>
          <input v-model="search" placeholder="Search users..."
            class="w-full border rounded-lg px-8 py-2 text-sm" />
        </div>
      </div>

      <p class="text-xs text-gray-400">{{ markedCount }} / {{ totalUsers }} users marked</p>

      <div class="flex gap-1.5 flex-wrap">
        <button v-for="f in filters" :key="f.key" @click="filterMode = f.key"
          class="px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-150"
          :class="filterMode === f.key ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'">
          {{ f.label }}
        </button>
      </div>

      <div class="bg-white rounded-xl border overflow-hidden">
        <div class="px-4 py-2.5 border-b border-gray-100 flex items-center justify-between text-xs">
          <span class="text-gray-500">
            Marked: <strong class="text-gray-700">{{ markedCount }}</strong> / {{ totalUsers }}
          </span>
          <span class="text-gray-400">{{ markedPercent }}%</span>
        </div>

        <div class="h-1.5 bg-gray-100">
          <div class="h-full bg-blue-500 transition-all duration-300" :style="{ width: markedPercent + '%' }"></div>
        </div>

        <div v-if="paginatedUsers.length === 0" class="px-4 py-8 text-sm text-gray-400 text-center">
          No users match
        </div>
        <div v-else class="divide-y divide-gray-50">
          <div v-for="u in paginatedUsers" :key="u.id"
            @click="canMark && isAttendanceOpen ? toggleAttendance(u.id) : null"
            class="flex items-center gap-3 px-4 py-2 transition-colors duration-150 select-none"
            :class="[savingUserId === u.id ? 'bg-green-50' : isMarked(u.id) ? 'bg-blue-50/30' : (canMark && isAttendanceOpen ? 'hover:bg-gray-50 cursor-pointer' : '')]">
            <span class="w-4 h-4 rounded border flex items-center justify-center text-xs font-bold transition-all duration-150 shrink-0"
              :class="isMarked(u.id) ? 'bg-blue-600 border-blue-600 text-white' : 'border-gray-300'">
              <span v-if="isMarked(u.id)">&#10003;</span>
            </span>
            <span class="text-sm flex-1 truncate">{{ u.name }}</span>
            <span class="text-xs px-1.5 py-0.5 rounded shrink-0"
              :class="u.voted ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-500'">
              {{ u.voted ? 'Voted' : 'No vote' }}
            </span>
          </div>
        </div>

        <div class="px-4 py-2.5 border-t border-gray-100 flex items-center justify-between text-xs text-gray-500">
          <button v-if="canMark && isAttendanceOpen && visibleUnmarkedCount > 0" @click.stop="markAllVisible"
            class="text-blue-600 hover:text-blue-800 font-medium">
            Mark all visible as present
          </button>
          <span v-else></span>
          <div class="flex items-center gap-2">
            <span>{{ pageStart }}-{{ pageEnd }} of {{ filteredUsers.length }}</span>
            <button @click="page = Math.max(1, page - 1)" :disabled="page <= 1"
              class="px-2 py-1 rounded border disabled:opacity-30 disabled:cursor-default hover:bg-gray-50">Prev</button>
            <button @click="page = Math.min(totalPages, page + 1)" :disabled="page >= totalPages"
              class="px-2 py-1 rounded border disabled:opacity-30 disabled:cursor-default hover:bg-gray-50">Next</button>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import api from '../api'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const attDate = ref(new Date().toISOString().split('T')[0])
const selectedMealType = ref('')
const mealTypes = ref([])
const users = ref([])
const attendanceList = ref([])
const savingUserId = ref(null)
const search = ref('')
const filterMode = ref('all')
const page = ref(1)
const pageSize = 50

const selectedMealTypeObj = computed(() => mealTypes.value.find(m => m.id === +selectedMealType.value))

function getAttendanceWindow(mt) {
  if (!mt || !mt.start_time || !mt.end_time || mt.attendance_buffer_hours == null) return null
  const d = new Date(attDate.value + 'T00:00:00')
  const [sh, sm] = mt.start_time.split(':')
  const [eh, em] = mt.end_time.split(':')
  const buf = mt.attendance_buffer_hours * 3600000
  const start = new Date(d.getTime() + (+sh * 3600000 + +sm * 60000) - buf)
  const end = new Date(d.getTime() + (+eh * 3600000 + +em * 60000) + buf)
  return { start, end }
}

const attendanceWindow = computed(() => getAttendanceWindow(selectedMealTypeObj.value))

const isAttendanceOpen = computed(() => {
  if (!attendanceWindow.value) return false
  const now = new Date()
  return now >= attendanceWindow.value.start && now < attendanceWindow.value.end
})

const attendanceWindowStart = computed(() => {
  if (!attendanceWindow.value) return ''
  return attendanceWindow.value.start.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })
})

const filters = [
  { key: 'all', label: 'All' },
  { key: 'marked', label: 'Marked' },
  { key: 'unmarked', label: 'Unmarked' },
  { key: 'voted', label: 'Voted' },
  { key: 'no-vote', label: 'No vote' },
]

const markedSet = computed(() => new Set(attendanceList.value.map(a => a.user_id)))
const markedCount = computed(() => markedSet.value.size)
const totalUsers = computed(() => users.value.length)
const markedPercent = computed(() => totalUsers.value ? Math.round(markedCount.value / totalUsers.value * 100) : 0)

const filteredUsers = computed(() => {
  let list = users.value
  const q = search.value.toLowerCase().trim()
  if (q) list = list.filter(u => u.name.toLowerCase().includes(q))
  switch (filterMode.value) {
    case 'marked': list = list.filter(u => markedSet.value.has(u.id)); break
    case 'unmarked': list = list.filter(u => !markedSet.value.has(u.id)); break
    case 'voted': list = list.filter(u => u.voted); break
    case 'no-vote': list = list.filter(u => !u.voted); break
  }
  return list
})

const totalPages = computed(() => Math.ceil(filteredUsers.value.length / pageSize) || 1)

const paginatedUsers = computed(() => {
  const start = (page.value - 1) * pageSize
  return filteredUsers.value.slice(start, start + pageSize)
})

const pageStart = computed(() => (page.value - 1) * pageSize + 1)
const pageEnd = computed(() => Math.min(page.value * pageSize, filteredUsers.value.length))

const visibleUnmarkedCount = computed(() => paginatedUsers.value.filter(u => !markedSet.value.has(u.id)).length)

function isMarked(userId) { return markedSet.value.has(userId) }

const canMark = computed(() => auth.isAdmin || hasDuty.value)
const hasDuty = ref(false)

async function loadUsers() {
  if (!selectedMealType.value) return
  page.value = 1
  try {
    const [uRes, aRes, vRes, dutyRes] = await Promise.all([
      api.get('/api/users/active'),
      api.get(`/api/attendance/date/${attDate.value}/${selectedMealType.value}`),
      api.get(`/api/votes/date/${attDate.value}`),
      api.get('/api/mess-duty/current').catch(() => ({ data: [] }))
    ])
    attendanceList.value = aRes.data
    const votedIds = new Set(vRes.data.filter(v => v.meal_type_id === +selectedMealType.value).map(v => v.user_id))
    users.value = uRes.data.map(u => ({ ...u, voted: votedIds.has(u.id) }))
    hasDuty.value = dutyRes.data.some(d => d.id === auth.user?.id)
  } catch (e) {
    console.error('Attendance load error:', e)
  }
}

watch([attDate, selectedMealType], loadUsers)

async function toggleAttendance(userId) {
  if (!canMark.value || !isAttendanceOpen.value) return
  try {
    savingUserId.value = userId
    const idx = attendanceList.value.findIndex(a => a.user_id === userId)
    if (idx >= 0) {
      await api.delete(`/api/attendance/${attendanceList.value[idx].id}`)
      attendanceList.value.splice(idx, 1)
    } else {
      const { data } = await api.post('/api/attendance', {
        user_id: userId, meal_type_id: +selectedMealType.value, date: attDate.value
      })
      attendanceList.value.push(data)
    }
  } catch (e) {
    alert(e.response?.data?.detail || 'Error')
  } finally {
    savingUserId.value = null
  }
}

async function markAllVisible() {
  if (!canMark.value || !isAttendanceOpen.value) return
  const ids = paginatedUsers.value.filter(u => !markedSet.value.has(u.id)).map(u => u.id)
  if (!ids.length) return
  try {
    await api.post('/api/attendance/batch', {
      meal_type_id: +selectedMealType.value, date: attDate.value, user_ids: ids
    })
    const { data } = await api.get(`/api/attendance/date/${attDate.value}/${selectedMealType.value}`)
    attendanceList.value = data
  } catch (e) {
    alert(e.response?.data?.detail || 'Error')
  }
}

function downloadCSV() {
  const mt = selectedMealTypeObj.value
  const rows = [['Name', 'Username', 'Voted', 'Marked Present']]
  for (const u of users.value) {
    rows.push([u.name, u.username, u.voted ? 'Yes' : 'No', isMarked(u.id) ? 'Yes' : 'No'])
  }
  const csv = rows.map(r => r.map(c => `"${c}"`).join(',')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url; a.download = `${attDate.value}-${mt?.name || 'attendance'}.csv`
  a.click(); URL.revokeObjectURL(url)
}

onMounted(async () => {
  try {
    const { data } = await api.get('/api/meal-types')
    mealTypes.value = data
    if (data.length) selectedMealType.value = String(data[0].id)
  } catch (e) {
    console.error('Attendance init error:', e)
  }
})
</script>
