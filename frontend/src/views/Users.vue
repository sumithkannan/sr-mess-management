<template>
  <div class="space-y-4">
    <h2 class="font-semibold">Manage Users</h2>

    <div class="bg-white rounded-xl border overflow-hidden">
      <div class="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
        <h3 class="font-medium text-sm text-gray-500 uppercase tracking-wide">Mess Duty Assignments</h3>
      </div>

      <div class="px-4 py-3 border-b border-gray-100 space-y-2">
        <div class="relative">
          <input v-model="dutySearch" placeholder="Search user..."
            class="w-full border rounded-lg px-3 py-2 text-sm" @input="dutySelectedUserId = null" />
          <div v-if="dutySearch && !dutySelectedUserId && dutySuggestions.length"
            class="absolute top-full left-0 right-0 mt-1 bg-white border rounded-lg shadow-lg z-10 max-h-48 overflow-y-auto">
            <button v-for="u in dutySuggestions" :key="u.id" @click="selectDutyUser(u)"
              class="w-full text-left px-3 py-2 text-sm hover:bg-gray-50 border-b last:border-0">
              {{ u.name }} <span class="text-gray-400">@{{ u.username }}</span>
            </button>
          </div>
        </div>
        <div class="flex gap-2">
          <input type="date" v-model="dutyStart" class="border rounded px-3 py-2 text-sm flex-1" />
          <input type="date" v-model="dutyEnd" class="border rounded px-3 py-2 text-sm flex-1" />
        </div>
        <div class="flex gap-2">
          <button @click="assignDuty"
            class="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 active:scale-95 transition-all duration-150 flex-1"
            :disabled="!canAssign">
            {{ editingDutyId ? 'Update Duty' : 'Assign Duty' }}
          </button>
          <button v-if="editingDutyId" @click="cancelDutyEdit"
            class="px-4 py-2 rounded-lg text-sm font-medium border border-gray-200 hover:bg-gray-50 transition-all duration-150">
            Cancel
          </button>
        </div>
      </div>

      <div class="px-4 py-3 border-b border-gray-100">
        <div class="flex gap-2 items-end">
          <div class="flex-1">
            <label class="text-xs text-gray-500 mb-1 block">Who was on duty?</label>
            <input type="date" v-model="lookupDate" class="w-full border rounded px-3 py-2 text-sm" />
          </div>
          <button @click="lookupDuty"
            class="px-4 py-2 rounded-lg text-sm font-medium border border-gray-200 hover:bg-gray-50 transition-all duration-150">
            Lookup
          </button>
        </div>
        <div v-if="lookupResult.length" class="mt-2 text-sm text-gray-700">
          <span class="font-medium">{{ lookupDateLabel }}</span>
          <ul class="mt-1 space-y-0.5">
            <li v-for="u in lookupResult" :key="u.id" class="text-gray-600">
              {{ u.name }} <span class="text-gray-400">({{ u.start_date }} → {{ u.end_date }})</span>
            </li>
          </ul>
        </div>
        <div v-else-if="lookupDate && lookedUp" class="mt-2 text-sm text-gray-400">
          No duty assigned on this date
        </div>
      </div>

      <div v-if="duties.length === 0" class="px-4 py-6 text-sm text-gray-400 text-center">No duty assignments</div>
      <div v-else class="divide-y divide-gray-50">
        <div v-for="d in duties" :key="d.id" class="flex items-center justify-between px-4 py-2.5">
          <div class="text-sm">
            <span class="font-medium text-gray-800">{{ getUserName(d.user_id) }}</span>
            <span class="text-gray-400 mx-1">—</span>
            <span class="text-gray-500">{{ d.start_date }} → {{ d.end_date }}</span>
          </div>
          <div class="flex gap-1.5">
            <button @click="editDuty(d)" class="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded hover:bg-blue-200">Edit</button>
            <button @click="removeDuty(d.id)" class="text-xs bg-red-100 text-red-700 px-2 py-1 rounded hover:bg-red-200">Remove</button>
          </div>
        </div>
      </div>
    </div>

    <div class="bg-white rounded-xl border overflow-hidden">
      <div class="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
        <h3 class="font-medium text-sm text-gray-500 uppercase tracking-wide">Users</h3>
        <button @click="showForm = !showForm" class="text-sm bg-blue-600 text-white px-3 py-1.5 rounded-lg hover:bg-blue-700 transition-all duration-150">
          {{ showForm ? 'Cancel' : '+ Add' }}
        </button>
      </div>

      <div v-if="showForm" class="px-4 py-3 border-b border-gray-100 space-y-2">
        <input v-model="form.username" placeholder="Username" class="w-full border rounded px-3 py-2 text-sm" />
        <input v-model="form.name" placeholder="Name" class="w-full border rounded px-3 py-2 text-sm" />
        <input v-model="form.email" placeholder="Email (optional)" type="email" class="w-full border rounded px-3 py-2 text-sm" />
        <p class="text-xs text-gray-400">Default password: PasswordToBeChanged</p>
        <button @click="addUser" class="bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-green-700 active:scale-95 transition-all duration-150"
          :disabled="!form.username || !form.name">
          Create User
        </button>
      </div>

      <div class="px-4 py-3 border-b border-gray-100 space-y-2">
        <input v-model="search" placeholder="Search name, username, email..."
          class="w-full border rounded-lg px-3 py-2 text-sm" />
        <div class="flex gap-1.5 flex-wrap">
          <button v-for="f in filters" :key="f.key" @click="filterMode = f.key; page = 1"
            class="px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-150"
            :class="filterMode === f.key ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'">
            {{ f.label }}
          </button>
        </div>
        <p class="text-xs text-gray-400">{{ filteredUsers.length }} user{{ filteredUsers.length === 1 ? '' : 's' }}</p>
      </div>

      <div v-if="paginatedUsers.length === 0" class="px-4 py-6 text-sm text-gray-400 text-center">No users match</div>
      <div v-else class="divide-y divide-gray-50">
        <div v-for="u in paginatedUsers" :key="u.id" class="flex items-center justify-between px-4 py-2">
          <div class="min-w-0 flex-1">
            <p class="text-sm font-medium text-gray-800 truncate">{{ u.name }}</p>
            <p class="text-xs text-gray-500 truncate">
              @{{ u.username }}
              <span class="px-1.5 py-0.5 rounded text-xs font-medium ml-1"
                :class="u.role === 'admin' ? 'bg-purple-100 text-purple-700' : 'bg-gray-100 text-gray-600'">
                {{ u.role }}
              </span>
              <span v-if="!u.is_active" class="text-red-500 ml-1">&#9888; Suspended</span>
            </p>
          </div>
          <div class="flex gap-1.5 shrink-0 ml-3">
            <button v-if="u.role !== 'admin'" @click="promote(u.id)"
              class="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded hover:bg-purple-200">Admin</button>
            <button @click="u.is_active ? suspend(u.id) : activate(u.id)"
              class="text-xs px-2 py-1 rounded"
              :class="u.is_active ? 'bg-red-100 text-red-700 hover:bg-red-200' : 'bg-green-100 text-green-700 hover:bg-green-200'">
              {{ u.is_active ? 'Suspend' : 'Activate' }}
            </button>
            <button @click="deleteUser(u.id)"
              class="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded hover:bg-gray-200">Del</button>
          </div>
        </div>
      </div>

      <div v-if="totalPages > 1" class="px-4 py-2.5 border-t border-gray-100 flex items-center justify-between text-xs text-gray-500">
        <span></span>
        <div class="flex items-center gap-2">
          <span>{{ pageStart }}-{{ pageEnd }} of {{ filteredUsers.length }}</span>
          <button @click="page = Math.max(1, page - 1)" :disabled="page <= 1"
            class="px-2 py-1 rounded border disabled:opacity-30 disabled:cursor-default hover:bg-gray-50">Prev</button>
          <button @click="page = Math.min(totalPages, page + 1)" :disabled="page >= totalPages"
            class="px-2 py-1 rounded border disabled:opacity-30 disabled:cursor-default hover:bg-gray-50">Next</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import api from '../api'

const users = ref([])
const duties = ref([])
const showForm = ref(false)
const form = ref({ username: '', name: '', email: '' })
const search = ref('')
const filterMode = ref('all')
const page = ref(1)
const pageSize = 50

const dutySearch = ref('')
const dutySelectedUserId = ref(null)
const dutySelectedUserName = ref('')
const dutyStart = ref('')
const dutyEnd = ref('')
const editingDutyId = ref(null)

const lookupDate = ref('')
const lookupResult = ref([])
const lookedUp = ref(false)

const filters = [
  { key: 'all', label: 'All' },
  { key: 'active', label: 'Active' },
  { key: 'suspended', label: 'Suspended' },
  { key: 'admins', label: 'Admins' },
]

const filteredUsers = computed(() => {
  let list = users.value
  const q = search.value.toLowerCase().trim()
  if (q) list = list.filter(u =>
    u.name.toLowerCase().includes(q) ||
    u.username.toLowerCase().includes(q) ||
    (u.email || '').toLowerCase().includes(q)
  )
  switch (filterMode.value) {
    case 'active': list = list.filter(u => u.is_active); break
    case 'suspended': list = list.filter(u => !u.is_active); break
    case 'admins': list = list.filter(u => u.role === 'admin'); break
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

const dutySuggestions = computed(() => {
  if (!dutySearch.value.trim() || dutySelectedUserId.value) return []
  const q = dutySearch.value.toLowerCase()
  return users.value.filter(u => u.is_active && u.name.toLowerCase().includes(q)).slice(0, 10)
})

const canAssign = computed(() => {
  return dutySelectedUserId.value && dutyStart.value && dutyEnd.value
})

const lookupDateLabel = computed(() => {
  if (!lookupDate.value) return ''
  const d = new Date(lookupDate.value + 'T00:00:00')
  return d.toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' })
})

function getUserName(userId) {
  const u = users.value.find(x => x.id === userId)
  return u ? u.name : 'User #' + userId
}

async function load() {
  try {
    const [u, d] = await Promise.all([api.get('/api/users'), api.get('/api/mess-duty')])
    users.value = u.data
    duties.value = d.data
  } catch (e) {
    console.error('Users load error:', e)
  }
}

function selectDutyUser(u) {
  dutySelectedUserId.value = u.id
  dutySelectedUserName.value = u.name
  dutySearch.value = u.name
}

function cancelDutyEdit() {
  editingDutyId.value = null
  dutySelectedUserId.value = null
  dutySelectedUserName.value = ''
  dutySearch.value = ''
  dutyStart.value = ''
  dutyEnd.value = ''
}

async function assignDuty() {
  if (!canAssign.value) return
  try {
    const payload = { user_id: dutySelectedUserId.value, start_date: dutyStart.value, end_date: dutyEnd.value }
    if (editingDutyId.value) {
      const { data } = await api.put(`/api/mess-duty/${editingDutyId.value}`, payload)
      const idx = duties.value.findIndex(d => d.id === editingDutyId.value)
      if (idx >= 0) duties.value[idx] = data
    } else {
      const { data } = await api.post('/api/mess-duty', payload)
      duties.value.push(data)
    }
    cancelDutyEdit()
  } catch (e) { alert(e.response?.data?.detail || 'Error') }
}

function editDuty(d) {
  editingDutyId.value = d.id
  dutySelectedUserId.value = d.user_id
  dutySearch.value = getUserName(d.user_id)
  dutyStart.value = d.start_date
  dutyEnd.value = d.end_date
}

async function removeDuty(id) {
  try {
    await api.delete(`/api/mess-duty/${id}`)
    duties.value = duties.value.filter(d => d.id !== id)
  } catch (e) { alert(e.response?.data?.detail || 'Error') }
}

async function lookupDuty() {
  if (!lookupDate.value) return
  lookedUp.value = true
  try {
    const { data } = await api.get(`/api/mess-duty/on-date/${lookupDate.value}`)
    lookupResult.value = data
  } catch (e) {
    lookupResult.value = []
    alert(e.response?.data?.detail || 'Error')
  }
}

async function addUser() {
  if (!form.value.username || !form.value.name) return
  try {
    const { data } = await api.post('/api/users', form.value)
    users.value.push(data)
    form.value = { username: '', name: '', email: '' }
    showForm.value = false
  } catch (e) { alert(e.response?.data?.detail || 'Error') }
}

async function promote(id) {
  try {
    await api.patch(`/api/users/${id}/role?role=admin`)
    const u = users.value.find(x => x.id === id)
    if (u) u.role = 'admin'
  } catch (e) { alert(e.response?.data?.detail || 'Error') }
}

async function suspend(id) {
  try {
    await api.patch(`/api/users/${id}/suspend`)
    const u = users.value.find(x => x.id === id)
    if (u) u.is_active = false
  } catch (e) { alert(e.response?.data?.detail || 'Error') }
}

async function activate(id) {
  try {
    await api.patch(`/api/users/${id}/activate`)
    const u = users.value.find(x => x.id === id)
    if (u) u.is_active = true
  } catch (e) { alert(e.response?.data?.detail || 'Error') }
}

async function deleteUser(id) {
  if (!confirm('Delete user?')) return
  try {
    await api.delete(`/api/users/${id}`)
    users.value = users.value.filter(u => u.id !== id)
  } catch (e) { alert(e.response?.data?.detail || 'Error') }
}

watch([search, filterMode], () => { page.value = 1 })

onMounted(load)
</script>
