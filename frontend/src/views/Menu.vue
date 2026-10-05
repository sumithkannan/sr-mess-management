<template>
  <div class="space-y-4">
    <div v-if="anyDirty" class="sticky top-0 z-10 bg-yellow-50 border border-yellow-200 rounded-lg px-4 py-2 text-sm text-yellow-700 flex items-center gap-2">
      <span class="w-2 h-2 rounded-full bg-yellow-500 inline-block"></span>
      You have unsaved changes
    </div>

    <h2 class="font-semibold">Menu</h2>

    <div class="flex gap-2">
      <input type="date" v-model="viewDate" @change="loadMenu" class="border rounded px-3 py-2 text-sm flex-1" />
      <button v-if="auth.isAdmin && hasOverrides" @click="clearDateOverrides" class="text-sm bg-red-100 text-red-600 px-3 py-2 rounded hover:bg-red-200">Clear Overrides</button>
    </div>

    <div class="bg-white rounded-xl border overflow-hidden">
      <div class="px-4 py-3 border-b border-gray-100 flex items-center justify-between cursor-pointer select-none"
        @click="dateExpanded = !dateExpanded">
        <h3 class="font-medium text-sm text-gray-500 uppercase tracking-wide">Menu for {{ formattedDate }}</h3>
        <div class="flex items-center gap-2">
          <span v-if="dateDirty" class="flex items-center gap-1 text-xs text-yellow-600">
            <span class="w-1.5 h-1.5 rounded-full bg-yellow-500"></span> Unsaved
          </span>
          <span v-else-if="dateSaved" class="text-xs text-green-600">Saved</span>
          <span class="text-xs text-gray-400">{{ dateExpanded ? '▼' : '▶' }}</span>
        </div>
      </div>

      <div v-if="dateExpanded">
        <div v-if="mealTypes.length === 0" class="px-4 py-8 text-center text-sm text-gray-400">No meal types configured.</div>
        <div v-else class="divide-y divide-gray-50">
          <div v-for="mt in mealTypes" :key="'d'+mt.id" class="px-4 py-3 flex items-center gap-3">
            <span class="text-xs font-medium w-16 text-gray-600">{{ mt.name }}</span>
            <template v-if="auth.isAdmin">
              <input v-model="dateDrafts[mt.id]"
                placeholder="Item name"
                class="border rounded px-2 py-1.5 text-sm flex-1 transition-colors duration-150"
                :class="dateFieldDirty(mt.id) ? 'border-yellow-300 bg-yellow-50' : 'border-gray-200'" />
            </template>
            <span v-else class="text-sm flex-1">{{ dateDrafts[mt.id] || '-' }}</span>
          </div>
        </div>

        <div v-if="auth.isAdmin" class="px-4 py-3 border-t border-gray-100 flex justify-end">
          <button @click="saveDateItems"
            class="px-4 py-2 rounded-lg text-sm font-medium transition-all duration-150"
            :class="dateDirty ? 'bg-yellow-500 text-white hover:bg-yellow-600 active:scale-95' : 'bg-gray-100 text-gray-400 cursor-default'"
            :disabled="!dateDirty">
            Save Date Menu
          </button>
        </div>
      </div>
    </div>

    <div class="bg-white rounded-xl border overflow-hidden">
      <div class="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
        <h3 class="font-medium text-sm text-gray-500 uppercase tracking-wide">Weekly Menu</h3>
        <span v-if="recurringDirty" class="flex items-center gap-1 text-xs text-yellow-600">
          <span class="w-1.5 h-1.5 rounded-full bg-yellow-500"></span> Unsaved
        </span>
        <span v-else-if="recurringSaved" class="text-xs text-green-600">Saved</span>
      </div>

      <div v-if="mealTypes.length === 0" class="px-4 py-8 text-center text-sm text-gray-400">No meal types configured.</div>
      <div v-else class="divide-y divide-gray-50">
        <div v-for="(day, di) in days" :key="di" class="px-4 py-3">
          <h4 class="text-xs font-semibold text-gray-700 mb-2 flex items-center gap-2">
            {{ day }}
            <span v-if="dayDirty(di)" class="w-1.5 h-1.5 rounded-full bg-yellow-500 inline-block"></span>
          </h4>
          <div v-for="mt in mealTypes" :key="mt.id" class="flex items-center gap-2 py-1.5">
            <span class="text-xs w-16 text-gray-500">{{ mt.name }}</span>
            <template v-if="auth.isAdmin">
              <input v-model="recurringInputs[mt.id + '-' + di]"
                placeholder="Item name"
                class="border rounded px-2 py-1.5 text-sm flex-1 transition-colors duration-150"
                :class="recurringFieldDirty(mt.id, di) ? 'border-yellow-300 bg-yellow-50' : 'border-gray-200'" />
            </template>
            <span v-else class="text-sm flex-1">{{ getRecurringItemName(mt.id, di) || '-' }}</span>
          </div>
        </div>
      </div>

      <div v-if="auth.isAdmin" class="px-4 py-3 border-t border-gray-100 flex justify-end">
        <button @click="saveRecurringItems"
          class="px-4 py-2 rounded-lg text-sm font-medium transition-all duration-150"
          :class="recurringDirty ? 'bg-yellow-500 text-white hover:bg-yellow-600 active:scale-95' : 'bg-gray-100 text-gray-400 cursor-default'"
          :disabled="!recurringDirty">
          Save Weekly Menu
        </button>
      </div>
    </div>

    <div v-if="!mealTypes.length" class="text-center py-8 text-gray-400 text-sm">
      No meal types configured.
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { onBeforeRouteLeave } from 'vue-router'
import api from '../api'
import { useAuthStore } from '../stores/auth'
const auth = useAuthStore()

const mealTypes = ref([])
const dateItems = ref([])
const recurringItems = ref([])
const viewDate = ref(new Date().toISOString().split('T')[0])
const days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
const recurringInputs = reactive({})

const dateDrafts = reactive({})
const dateOriginals = reactive({})
const recurringOriginals = reactive({})
const dateExpanded = ref(false)
const dateSaved = ref(false)
const recurringSaved = ref(false)

const formattedDate = computed(() => {
  const d = new Date(viewDate.value + 'T00:00:00')
  return d.toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short' })
})

const hasOverrides = computed(() => dateItems.value.length > 0)

const dateDirty = computed(() => {
  return mealTypes.value.some(mt => (dateDrafts[mt.id] ?? '') !== (dateOriginals[mt.id] ?? ''))
})

const recurringDirty = computed(() => {
  return mealTypes.value.some(mt =>
    days.some((_, di) => {
      const key = mt.id + '-' + di
      return (recurringInputs[key] ?? '') !== (recurringOriginals[key] ?? '')
    })
  )
})

const anyDirty = computed(() => dateDirty.value || recurringDirty.value)

function dateFieldDirty(mtId) {
  return (dateDrafts[mtId] ?? '') !== (dateOriginals[mtId] ?? '')
}

function dayDirty(di) {
  return mealTypes.value.some(mt => recurringFieldDirty(mt.id, di))
}

function recurringFieldDirty(mtId, dow) {
  const key = mtId + '-' + dow
  return (recurringInputs[key] ?? '') !== (recurringOriginals[key] ?? '')
}

async function loadMenu() {
  try {
    const [mt, di, ri] = await Promise.all([
      api.get('/api/meal-types'),
      api.get(`/api/menu-items/date/${viewDate.value}`),
      api.get('/api/menu-items/recurring')
    ])
    mealTypes.value = mt.data
    dateItems.value = di.data.filter(item => item.date !== null)
    recurringItems.value = ri.data
    dateSaved.value = false
    recurringSaved.value = false

    for (const mtItem of mt.data) {
      const item = dateItems.value.find(i => i.meal_type_id === mtItem.id)
      const name = item ? item.item_name : ''
      dateOriginals[mtItem.id] = name
      dateDrafts[mtItem.id] = name
    }

    for (const item of ri.data) {
      const key = item.meal_type_id + '-' + item.day_of_week
      recurringInputs[key] = item.item_name
      recurringOriginals[key] = item.item_name
    }

    for (const mtItem of mt.data) {
      for (let di = 0; di < 7; di++) {
        const key = mtItem.id + '-' + di
        if (!(key in recurringOriginals)) {
          recurringOriginals[key] = ''
          if (!(key in recurringInputs)) {
            recurringInputs[key] = ''
          }
        }
      }
    }
  } catch (e) {
    console.error('Menu load error:', e)
  }
}

function getRecurringItemName(mtId, dow) {
  const item = recurringItems.value.find(i => i.meal_type_id === mtId && i.day_of_week === dow)
  return item ? item.item_name : ''
}

async function saveDateItems() {
  const promises = []
  for (const mt of mealTypes.value) {
    const draft = dateDrafts[mt.id]
    const original = dateOriginals[mt.id]
    if ((draft ?? '') === (original ?? '')) continue
    if (!draft || !draft.trim()) continue
    promises.push(
      api.post('/api/menu-items', {
        meal_type_id: mt.id,
        item_name: draft,
        date: viewDate.value,
        is_recurring: false
      }).then(({ data }) => {
        const idx = dateItems.value.findIndex(i => i.meal_type_id === mt.id)
        if (idx >= 0) dateItems.value[idx] = data
        else dateItems.value.push(data)
        dateOriginals[mt.id] = draft
      })
    )
  }
  try {
    await Promise.all(promises)
    dateSaved.value = true
  } catch (e) { alert('Error: ' + (e.response?.data?.detail || e.message)) }
}

async function saveRecurringItems() {
  const promises = []
  for (const mt of mealTypes.value) {
    for (let di = 0; di < 7; di++) {
      const key = mt.id + '-' + di
      const draft = recurringInputs[key]
      const original = recurringOriginals[key]
      if ((draft ?? '') === (original ?? '')) continue
      if (!draft || !draft.trim()) continue
      promises.push(
        api.post('/api/menu-items', {
          meal_type_id: mt.id,
          item_name: draft,
          day_of_week: di,
          is_recurring: true
        }).then(({ data }) => {
          const idx = recurringItems.value.findIndex(i => i.meal_type_id === mt.id && i.day_of_week === di)
          if (idx >= 0) recurringItems.value[idx] = data
          else recurringItems.value.push(data)
          recurringOriginals[key] = draft
        })
      )
    }
  }
  try {
    await Promise.all(promises)
    recurringSaved.value = true
  } catch (e) { alert('Error: ' + (e.response?.data?.detail || e.message)) }
}

async function clearDateOverrides() {
  try {
    for (const item of dateItems.value) {
      await api.delete(`/api/menu-items/${item.id}`)
    }
    await loadMenu()
  } catch (e) { alert('Error: ' + (e.response?.data?.detail || e.message)) }
}

function warnUnsaved(e) {
  if (anyDirty.value) {
    e.preventDefault()
    e.returnValue = ''
  }
}

onBeforeRouteLeave((to, from, next) => {
  if (anyDirty.value && !confirm('You have unsaved changes. Discard them?')) {
    next(false)
  } else {
    next()
  }
})

watch(anyDirty, (v) => {
  if (v) window.addEventListener('beforeunload', warnUnsaved)
  else window.removeEventListener('beforeunload', warnUnsaved)
})

watch(dateDirty, (v) => { if (v) dateSaved.value = false })
watch(recurringDirty, (v) => { if (v) recurringSaved.value = false })

onMounted(loadMenu)
</script>
