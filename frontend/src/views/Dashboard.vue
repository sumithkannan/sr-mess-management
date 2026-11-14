<template>
  <div class="space-y-4">
    <div v-if="loading" class="space-y-4">
      <div class="h-12 bg-white rounded-lg border animate-pulse"></div>
      <SkeletonCard v-for="i in 2" :key="i" />
    </div>
    <template v-else>
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
      <button @click="changeDate(-1)"
        class="text-lg text-gray-500 hover:text-gray-800 leading-none w-7 text-center">&#8249;</button>
      <div class="flex-1 text-center">
        <p class="text-xs text-gray-400">Menu for</p>
        <span @click="$refs.dateInput?.showPicker?.() || $refs.dateInput?.click()"
          class="text-sm font-semibold text-gray-800 cursor-pointer select-none">
          {{ formattedDate }}
        </span>
        <p v-if="dateVotingStatus !== 'open'" class="text-xs"
          :class="dateVotingStatus === 'upcoming' ? 'text-orange-600' : 'text-gray-500'">
          {{ dateVotingStatus === 'upcoming' ? 'Voting not open' : 'Voting closed' }}
        </p>
      </div>
      <button @click="changeDate(1)"
        class="text-lg text-gray-500 hover:text-gray-800 leading-none w-7 text-center">&#8250;</button>
      <input ref="dateInput" type="date" v-model="selectedDate" @change="pickDate"
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
        <p v-if="itemsText(mt.id)" class="text-base font-medium text-gray-800 text-center">{{ itemsText(mt.id) }}</p>
        <p v-else class="text-sm text-gray-400 text-center italic">No menu available</p>
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
          <div class="flex items-center justify-between gap-2 mt-1.5 text-xs">
            <span class="text-gray-400">Tap to vote</span>
            <span class="font-medium tabular-nums text-green-700">{{ voteCountdown(mt) }}</span>
          </div>
          <p class="text-[11px] text-gray-400 mt-0.5 text-center">Vote by {{ voteDeadline(mt) }}</p>
        </template>
        <template v-else>
          <p class="text-sm text-center font-medium"
            :class="isMealVoted(mt) ? 'text-blue-600' : 'text-gray-400'">
            {{ isMealVoted(mt) ? '✓ You voted' : (getVotingStatus(mt) === 'upcoming' ? 'Voting opens soon' : 'Did not vote') }}
          </p>
          <p class="text-xs text-gray-400 mt-1 text-center">{{ votingSubtext(mt) }}</p>
        </template>
      </div>

      <div v-if="!isVotingOpen(mt) && itemsText(mt.id)" class="px-4 py-3">
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
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import api from '../api'
import { useToast } from '../composables/useToast'
import SkeletonCard from '../components/SkeletonCard.vue'
import { todayStr, zonedTimestamp, formatCountdown, APP_TIMEZONE } from '../utils/time'

const toast = useToast()
const loading = ref(true)
const selectedDate = ref(todayStr())
const mealTypes = ref([])
const menuItems = ref([])
const votes = ref([])
const myRatings = ref({})
const hoverRating = reactive({})
const dutyUsers = ref([])
const offDays = ref([])

// Ticks once a second so vote badges and countdowns stay live.
const now = ref(Date.now())
let nowTimer = null

const offDayToday = computed(() => {
  return offDays.value.find(o => selectedDate.value >= o.start_date && selectedDate.value <= o.end_date) || null
})

const upcomingOffDays = computed(() => {
  const today = todayStr()
  return offDays.value.filter(o => o.start_date > today).slice(0, 5)
})

const formattedDate = computed(() => {
  const d = new Date(selectedDate.value + 'T00:00:00')
  return d.toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short' })
})

// Voting state for the selected date as a whole: 'open' when at least one
// meal's voting window contains the current time, 'upcoming' when voting for
// the date has not started yet, otherwise 'closed' (deadline passed).
function dateVotingStatusOf(dateStr) {
  if (offDays.value.find(o => dateStr >= o.start_date && dateStr <= o.end_date)) return 'closed'
  const t = now.value
  let earliestOpen = null
  for (const mt of mealTypes.value) {
    if (!mt.start_time || mt.vote_cutoff_hours == null || mt.vote_open_interval_days == null) continue
    const open = zonedTimestamp(dateStr) - mt.vote_open_interval_days * 86400000
    const [h, m] = mt.start_time.split(':').map(Number)
    const deadline = zonedTimestamp(dateStr, h, m) - mt.vote_cutoff_hours * 3600000
    if (t >= open && t < deadline) return 'open'
    if (earliestOpen === null || open < earliestOpen) earliestOpen = open
  }
  if (earliestOpen === null) return 'closed'
  return t < earliestOpen ? 'upcoming' : 'closed'
}

const dateVotingStatus = computed(() => dateVotingStatusOf(selectedDate.value))

async function loadData() {
  loading.value = true
  try {
    const { data } = await api.get('/api/dashboard', { params: { date: selectedDate.value } })
    mealTypes.value = (data.meal_types || []).filter(m => m.is_active)
    menuItems.value = data.menu_items || []
    votes.value = data.my_votes || []
    myRatings.value = {}
    for (const r of (data.my_ratings || [])) myRatings.value[r.menu_item_id] = r.rating
    dutyUsers.value = (data.mess_duty || []).map(d => d.name)
    offDays.value = data.off_days || []
  } catch (e) {
    console.error('Dashboard load error:', e)
  } finally {
    loading.value = false
  }
}

function isDateVotingOpen(dateStr) {
  return dateVotingStatusOf(dateStr) === 'open'
}

function changeDate(delta) {
  selectedDate.value = shiftDate(selectedDate.value, delta)
  loadData()
}

onMounted(async () => {
  nowTimer = setInterval(() => { now.value = Date.now() }, 1000)
  await loadData()
  // ensure we start on a vote-open date if possible
  if (!isDateVotingOpen(selectedDate.value)) {
    const today = todayStr()
    if (isDateVotingOpen(today)) {
      selectedDate.value = today
      await loadData()
    }
  }
})

onUnmounted(() => {
  if (nowTimer) clearInterval(nowTimer)
})

function pickDate() {
  const picked = dateInput.value?.value
  if (picked && picked !== selectedDate.value) {
    selectedDate.value = picked
    loadData()
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
  const open = new Date(zonedTimestamp(selectedDate.value) - mt.vote_open_interval_days * 86400000)
  const [h, m] = mt.start_time.split(':').map(Number)
  const deadline = new Date(zonedTimestamp(selectedDate.value, h, m) - mt.vote_cutoff_hours * 3600000)
  return { open, deadline }
}

function isVotingOpen(mt) {
  if (offDayToday.value) return false
  const win = getVoteWindow(mt)
  if (!win) return false
  const t = now.value
  return t >= win.open.getTime() && t < win.deadline.getTime()
}

function getRatingStart(mt) {
  if (!mt.end_time || mt.rating_start_hours == null) return null
  const [h, m] = mt.end_time.split(':').map(Number)
  return new Date(zonedTimestamp(selectedDate.value, h, m) + mt.rating_start_hours * 3600000)
}

function isRatingOpen(mt) {
  const start = getRatingStart(mt)
  if (!start) return false
  return now.value >= start.getTime()
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
  return now.value < win.open.getTime() ? 'upcoming' : 'closed'
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

// "7:00 am", prefixed with the date when it is not the selected date.
function formatVoteDeadline(date) {
  const day = date.toLocaleDateString('en-IN', { timeZone: APP_TIMEZONE })
  const selectedDay = new Date(zonedTimestamp(selectedDate.value)).toLocaleDateString('en-IN', { timeZone: APP_TIMEZONE })
  const time = date.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', timeZone: APP_TIMEZONE })
  if (day === selectedDay) return time
  const label = date.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', timeZone: APP_TIMEZONE })
  return `${time} on ${label}`
}

// Time left to vote, based on the deadline computed from the admin settings
// (meal start minus `vote_cutoff_hours`).
function voteCountdown(mt) {
  const win = getVoteWindow(mt)
  if (!win || !isVotingOpen(mt)) return ''
  return `Closes in ${formatCountdown(win.deadline.getTime() - now.value)}`
}

// The computed deadline itself, shown against every meal.
function voteDeadline(mt) {
  const win = getVoteWindow(mt)
  return win ? formatVoteDeadline(win.deadline) : ''
}

function votingSubtext(mt) {
  const win = getVoteWindow(mt)
  if (!win) return ''
  if (offDayToday.value) return 'Mess closed'
  if (now.value < win.open.getTime()) {
    const opts = { weekday: 'short', day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit', timeZone: APP_TIMEZONE }
    return `Opens ${win.open.toLocaleDateString('en-IN', opts)}`
  }
  return `Voting closed at ${formatVoteDeadline(win.deadline)}`
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
  } catch (e) { toast.error(e.response?.data?.detail || 'Error') }
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
  } catch (e) { toast.error(e.response?.data?.detail || 'Error') }
}
</script>
