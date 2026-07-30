<template>
  <div class="space-y-4">
    <div v-if="dutyUsers.length" class="bg-green-50 border border-green-200 rounded-lg p-3">
      <p class="text-sm font-medium text-green-700">Mess Duty Today:</p>
      <p class="text-sm text-green-600">{{ dutyUsers.join(', ') }}</p>
    </div>

    <div v-if="offDayToday" class="bg-red-50 border border-red-200 rounded-lg p-3">
      <p class="text-sm font-medium text-red-700">Mess is Closed — {{ offDayToday.reason || 'Day Off' }}</p>
      <p v-if="offDayToday.start_date !== offDayToday.end_date" class="text-sm text-red-600">
        From {{ offDayToday.start_date }} to {{ offDayToday.end_date }}
      </p>
    </div>

    <div v-if="upcomingOffDays.length" class="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
      <p class="text-sm font-medium text-yellow-700">Upcoming Off Days:</p>
      <p v-for="o in upcomingOffDays" :key="o.id" class="text-sm text-yellow-600">
        {{ o.start_date }}<span v-if="o.start_date !== o.end_date"> – {{ o.end_date }}</span>
        <span v-if="o.reason"> ({{ o.reason }})</span>
      </p>
    </div>

    <div class="flex items-center gap-2 bg-white border rounded-lg px-3 py-2 shadow-sm">
      <button @click="selectedDate = shiftDate(selectedDate, -1); loadData()"
        class="text-lg text-gray-500 hover:text-gray-800 leading-none w-7 text-center">&#8249;</button>
      <div class="flex-1 text-center">
        <p class="text-xs text-gray-400">Menu for</p>
        <span @click="$refs.dateInput?.showPicker?.() || $refs.dateInput?.click()"
          class="text-sm font-semibold text-gray-800 cursor-pointer select-none">
          {{ formattedDate }}
        </span>
      </div>
      <button @click="selectedDate = shiftDate(selectedDate, 1); loadData()"
        class="text-lg text-gray-500 hover:text-gray-800 leading-none w-7 text-center">&#8250;</button>
      <input ref="dateInput" type="date" v-model="selectedDate" @change="loadData"
        class="w-0 p-0 border-0 opacity-0 absolute" />
    </div>

    <div v-for="mt in mealTypes" :key="mt.id" class="bg-white rounded-xl shadow-sm overflow-hidden transition-all duration-200"
      :class="cardMuted(mt) ? 'border border-gray-200 opacity-60' : 'border border-gray-200'">
      <div class="flex justify-between items-center px-4 py-3 border-b border-gray-100">
        <div>
          <h3 class="font-semibold text-gray-900">{{ mt.name }}</h3>
          <p v-if="mt.start_time" class="text-xs text-gray-500">{{ mt.start_time.substring(0,5) }} – {{ mt.end_time?.substring(0,5) }}</p>
        </div>
        <span class="text-xs px-2.5 py-1 rounded-full font-medium"
          :class="votingBadgeClass(mt)">
          {{ votingBadgeText(mt) }}
        </span>
      </div>

      <div class="px-4 py-3 border-b border-gray-50">
        <p class="text-base font-medium text-gray-800 text-center">{{ itemsText(mt.id) }}</p>
      </div>

      <div v-if="itemsText(mt.id)" class="px-4 py-3 border-b border-gray-50">
        <template v-if="isVotingOpen(mt)">
          <div class="flex gap-3">
            <button @click="setVote(mt, false)"
              :class="voteBtnClass(mt, false)"
              class="flex-1 py-2.5 rounded-xl text-sm font-medium transition-all duration-150">
              Not Voting
            </button>
            <button @click="setVote(mt, true)"
              :class="voteBtnClass(mt, true)"
              class="flex-1 py-2.5 rounded-xl text-sm font-medium transition-all duration-150">
              Voted ✓
            </button>
          </div>
          <p class="text-xs text-gray-400 mt-1.5 text-center">Tap to vote</p>
        </template>
        <template v-else>
          <p class="text-sm text-center font-medium"
            :class="isMealVoted(mt) ? 'text-blue-600' : 'text-gray-400'">
            {{ isMealVoted(mt) ? '✓ You voted' : (getVotingStatus(mt) === 'upcoming' ? 'Voting opens soon' : 'Did not vote') }}
          </p>
          <p class="text-xs text-gray-400 mt-1 text-center">{{ votingSubtext(mt) }}</p>
        </template>
      </div>

      <div v-if="!isVotingOpen(mt)" class="px-4 py-3">
        <div class="flex items-center justify-center gap-1"
          :class="canRate(mt) ? '' : 'pointer-events-none'"
          @mouseleave="onStarLeave(mt)">
          <span v-for="s in 5" :key="s"
            @click="submitRating(mt, s)"
            @mouseenter="onStarEnter(mt, s)"
            class="text-2xl transition-colors duration-100 select-none"
            :class="starClass(mt, s)">
            ★
          </span>
        </div>
        <p class="text-xs mt-1 text-center" :class="ratingHintClass(mt)">
          {{ ratingHint(mt) }}
        </p>
      </div>
    </div>

    <div v-if="!mealTypes.length" class="text-center py-8 text-gray-400 text-sm">
      No meal types configured.
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import api from '../api'

const selectedDate = ref(new Date().toISOString().split('T')[0])
const mealTypes = ref([])
const menuItems = ref([])
const votes = ref([])
const myRatings = ref({})
const hoverRating = reactive({})
const dutyUsers = ref([])
const offDays = ref([])

const offDayToday = computed(() => {
  return offDays.value.find(o => selectedDate.value >= o.start_date && selectedDate.value <= o.end_date) || null
})

const upcomingOffDays = computed(() => {
  const today = new Date().toISOString().split('T')[0]
  return offDays.value.filter(o => o.start_date > today).slice(0, 5)
})

const formattedDate = computed(() => {
  const d = new Date(selectedDate.value + 'T00:00:00')
  return d.toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short' })
})

async function loadData() {
  try {
    const [mtRes, miRes, vRes, rRes, dutyRes, offRes] = await Promise.all([
      api.get('/api/meal-types'),
      api.get(`/api/menu-items/date/${selectedDate.value}`),
      api.get(`/api/votes/my/${selectedDate.value}`),
      api.get(`/api/ratings/my/${selectedDate.value}`),
      api.get('/api/mess-duty/current'),
      api.get('/api/off-days')
    ])
    mealTypes.value = mtRes.data.filter(m => m.is_active)
    menuItems.value = miRes.data
    votes.value = vRes.data
    myRatings.value = {}
    for (const r of rRes.data) {
      myRatings.value[r.menu_item_id] = r.rating
    }
    dutyUsers.value = dutyRes.data.map(d => d.name)
    offDays.value = offRes.data
  } catch (e) {
    console.error('Dashboard load error:', e)
  }
}

function getMenuItems(mtId) {
  return menuItems.value.filter(i => i.meal_type_id === mtId)
}

function firstItemId(mtId) {
  const items = getMenuItems(mtId)
  return items.length ? items[0].id : 0
}

function itemsText(mtId) {
  const names = getMenuItems(mtId).map(i => i.item_name)
  return names.join(' + ')
}

function isMealVoted(mt) {
  return votes.value.some(v => v.meal_type_id === mt.id)
}

function shiftDate(dateStr, delta) {
  const d = new Date(dateStr + 'T00:00:00')
  d.setDate(d.getDate() + delta)
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

function getVoteWindow(mt) {
  if (!mt.start_time || mt.vote_cutoff_hours == null || mt.vote_open_interval_days == null) return null
  const mealDate = new Date(selectedDate.value + 'T00:00:00')
  const open = new Date(mealDate.getTime() - mt.vote_open_interval_days * 86400000)
  const [h, m] = mt.start_time.split(':')
  mealDate.setHours(+h, +m, 0, 0)
  const deadline = new Date(mealDate.getTime() - mt.vote_cutoff_hours * 3600000)
  return { open, deadline }
}

function isVotingOpen(mt) {
  if (offDayToday.value) return false
  const win = getVoteWindow(mt)
  if (!win) return false
  const now = new Date()
  return now >= win.open && now < win.deadline
}

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

function cardMuted(mt) {
  if (getVotingStatus(mt) === 'upcoming') return false
  return !isVotingOpen(mt) && !isRatingOpen(mt)
}

function canRate(mt) {
  return isRatingOpen(mt) && isMealVoted(mt)
}

function getVotingStatus(mt) {
  if (isVotingOpen(mt)) return 'open'
  const win = getVoteWindow(mt)
  if (!win) return 'closed'
  return new Date() < win.open ? 'upcoming' : 'closed'
}

function votingBadgeClass(mt) {
  const s = getVotingStatus(mt)
  if (s === 'open') return 'bg-green-100 text-green-700'
  if (s === 'upcoming') return 'bg-yellow-100 text-yellow-700'
  return 'bg-gray-100 text-gray-500'
}

function votingBadgeText(mt) {
  const s = getVotingStatus(mt)
  if (s === 'open') return 'Open'
  if (s === 'upcoming') return 'Opens soon'
  return 'Closed'
}

function votingSubtext(mt) {
  const win = getVoteWindow(mt)
  if (!win) return ''
  const now = new Date()
  if (now < win.open) {
    const opts = { weekday: 'short', day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }
    return `Opens ${win.open.toLocaleDateString('en-IN', opts)}`
  }
  return 'Voting closed'
}

function voteBtnClass(mt, isVoteBtn) {
  if (!isVotingOpen(mt)) return 'bg-gray-100 text-gray-400 border border-gray-200'
  const voted = isMealVoted(mt)
  if (isVoteBtn) return voted ? 'bg-blue-600 text-white border border-blue-600' : 'bg-gray-100 text-gray-500 border border-gray-200'
  return voted ? 'bg-gray-100 text-gray-500 border border-gray-200' : 'bg-blue-600 text-white border border-blue-600'
}

function ratingHint(mt) {
  const itemId = firstItemId(mt.id)
  if (!itemId) return ''
  if (isVotingOpen(mt)) return 'Vote now, rate later'
  if (!isRatingOpen(mt)) {
    const start = getRatingStart(mt)
    if (start) return `Rating opens ${start.toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short' })} ${start.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}`
    return ''
  }
  if (!isMealVoted(mt)) return 'Vote first to rate'
  if (myRatings.value[itemId]) return `Tap to update — ${'★'.repeat(myRatings.value[itemId])}${'☆'.repeat(5 - myRatings.value[itemId])}`
  return 'Tap a star to rate'
}

function ratingHintClass(mt) {
  if (myRatings.value[firstItemId(mt.id)] && isRatingOpen(mt)) return 'text-yellow-600'
  return 'text-gray-400'
}

function starClass(mt, s) {
  const itemId = firstItemId(mt.id)
  const effective = hoverRating[itemId] || myRatings.value[itemId] || 0
  return s <= effective ? 'text-yellow-400' : 'text-gray-300'
}

function onStarEnter(mt, s) {
  if (!canRate(mt)) return
  hoverRating[firstItemId(mt.id)] = s
}

function onStarLeave(mt) {
  if (!canRate(mt)) return
  hoverRating[firstItemId(mt.id)] = 0
}

async function setVote(mt, shouldVote) {
  try {
    if (shouldVote) {
      const item = getMenuItems(mt.id)[0]
      if (!item) return
      if (!isMealVoted(mt)) {
        const { data } = await api.post('/api/votes', {
          menu_item_id: item.id, meal_type_id: mt.id, vote_date: selectedDate.value
        })
        votes.value.push(data)
      }
    } else {
      const v = votes.value.find(x => x.meal_type_id === mt.id)
      if (v) {
        await api.delete(`/api/votes/${v.id}`)
        votes.value = votes.value.filter(x => x.id !== v.id)
      }
    }
  } catch (e) { alert(e.response?.data?.detail || 'Error') }
}

async function submitRating(mt, rating) {
  const itemId = firstItemId(mt.id)
  if (!itemId || !canRate(mt)) return
  try {
    await api.post('/api/ratings', {
      menu_item_id: itemId, meal_type_id: mt.id, date: selectedDate.value, rating
    })
    myRatings.value[itemId] = rating
    hoverRating[itemId] = 0
  } catch (e) { alert(e.response?.data?.detail || 'Error') }
}

onMounted(loadData)
</script>
