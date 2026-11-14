<template>
  <div class="space-y-4">
    <h2 class="font-semibold">Reports</h2>
    <div class="bg-white rounded-lg border p-4 space-y-3">
      <div class="flex gap-2">
        <input type="date" v-model="dateFrom" class="border rounded px-3 py-2 text-sm flex-1" />
        <input type="date" v-model="dateTo" class="border rounded px-3 py-2 text-sm flex-1" />
      </div>
      <div class="flex gap-2 flex-wrap">
        <button v-for="r in reportTypes" :key="r.key" @click="loadReport(r.key)"
          class="text-sm px-3 py-2 rounded transition"
          :class="activeReport === r.key ? 'bg-blue-600 text-white' : 'bg-gray-200 hover:bg-gray-300'">
          {{ r.label }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="text-center py-8 text-gray-400">Loading...</div>

    <div v-if="reportData.length && !loading" class="bg-white rounded-lg border p-4 space-y-3">
      <!-- Filters -->
      <div class="flex flex-wrap gap-2 items-center">
        <input v-model="searchQuery" placeholder="Filter (type to search)..."
          class="border rounded px-3 py-2 text-sm flex-1 min-w-[180px]" />
        <select v-if="activeReport === 'vote_vs_attendance'" v-model="filterMeal"
          class="border rounded px-3 py-2 text-sm">
          <option value="">All meals</option>
          <option v-for="m in mealTypes" :key="m.id" :value="m.name">{{ m.name }}</option>
        </select>
        <select v-if="activeReport === 'vote_vs_attendance'" v-model="filterUser"
          class="border rounded px-3 py-2 text-sm">
          <option value="">All users</option>
          <option v-for="u in users" :key="u.id" :value="u.name">{{ u.name }}</option>
        </select>
        <select v-model="pageSize" class="border rounded px-3 py-2 text-sm">
          <option :value="25">25 / page</option>
          <option :value="50">50 / page</option>
          <option :value="100">100 / page</option>
          <option :value="999999">All</option>
        </select>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-gray-50">
            <tr>
              <th v-for="h in reportHeaders" :key="h" class="px-3 py-2.5 text-left font-medium">{{ h }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, i) in pagedData" :key="i" class="border-t hover:bg-gray-50">
              <td v-for="(val, j) in row" :key="j" class="px-3 py-2">{{ val }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Paging -->
      <div v-if="totalPages > 1" class="flex items-center justify-between text-sm">
        <span class="text-gray-500">
          {{ filteredData.length }} rows · page {{ currentPage }} of {{ totalPages }}
        </span>
        <div class="flex gap-1">
          <button @click="currentPage = Math.max(1, currentPage - 1)" :disabled="currentPage <= 1"
            class="px-2 py-1 rounded border disabled:opacity-30 disabled:cursor-default hover:bg-gray-50">Prev</button>
          <button v-for="p in pageNumbers" :key="p" @click="currentPage = p"
            class="px-2 py-1 rounded border"
            :class="p === currentPage ? 'bg-blue-600 text-white border-blue-600' : 'hover:bg-gray-50'">
            {{ p }}
          </button>
          <button @click="currentPage = Math.min(totalPages, currentPage + 1)" :disabled="currentPage >= totalPages"
            class="px-2 py-1 rounded border disabled:opacity-30 disabled:cursor-default hover:bg-gray-50">Next</button>
        </div>
      </div>
    </div>

    <div v-if="noData && !loading" class="text-center py-8 text-gray-400">No data for selected period</div>

    <button v-if="reportData.length && !loading" @click="downloadPdf"
      class="bg-red-600 text-white px-4 py-2.5 rounded text-sm w-full hover:bg-red-700">
      Download PDF
    </button>
  </div>
</template>

<script setup>
const toast = useToast()
import { ref, computed, watch } from 'vue'
import api from '../api'
import { useToast } from '../composables/useToast'
import { todayStr } from '../utils/time'

const dateFrom = ref(todayStr(new Date(Date.now() - 7*86400000)))
const dateTo = ref(todayStr())
const activeReport = ref('')
const reportData = ref([])
const reportHeaders = ref([])
const loading = ref(false)
const noData = ref(false)
const currentReportType = ref('')

const mealTypes = ref([])
const users = ref([])

const searchQuery = ref('')
const filterMeal = ref('')
const filterUser = ref('')
const pageSize = ref(50)
const currentPage = ref(1)

const reportTypes = [
  { key: 'vote_vs_attendance', label: 'Vote vs Eat' },
  { key: 'meal_summary', label: 'Meal Summary' },
  { key: 'ratings_summary', label: 'Ratings' },
]

async function loadMeta() {
  try {
    const [mt, u] = await Promise.all([
      api.get('/api/meal-types'),
      api.get('/api/users/active').catch(() => ({ data: [] }))
    ])
    mealTypes.value = mt.data
    users.value = u.data
  } catch (e) { /* ignore */ }
}
loadMeta()

const filteredData = computed(() => {
  let rows = reportData.value
  if (activeReport.value === 'vote_vs_attendance') {
    if (filterMeal.value) rows = rows.filter(r => r[1] === filterMeal.value)
    if (filterUser.value) rows = rows.filter(r => r[2] === filterUser.value)
  }
  const q = searchQuery.value.trim().toLowerCase()
  if (q) {
    rows = rows.filter(row => row.some(cell => String(cell).toLowerCase().includes(q)))
  }
  return rows
})

const totalPages = computed(() => Math.max(1, Math.ceil(filteredData.value.length / pageSize.value)))
const pagedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredData.value.slice(start, start + pageSize.value)
})

const pageNumbers = computed(() => {
  const total = totalPages.value
  const cur = currentPage.value
  const pages = []
  const start = Math.max(1, cur - 2)
  const end = Math.min(total, cur + 2)
  for (let p = start; p <= end; p++) pages.push(p)
  return pages
})

watch([searchQuery, filterMeal, filterUser, pageSize, reportData], () => {
  currentPage.value = 1
})

async function loadReport(key) {
  activeReport.value = key
  currentReportType.value = key
  loading.value = true; noData.value = false
  searchQuery.value = ''
  filterMeal.value = ''
  filterUser.value = ''
  try {
    const { data } = await api.get(`/api/reports/${key.replace(/_/g, '-')}`, {
      params: { date_from: dateFrom.value, date_to: dateTo.value }
    })
    if (!data.length) { noData.value = true; reportData.value = []; return }
    if (key === 'vote_vs_attendance') {
      reportHeaders.value = ['Date', 'Meal', 'Name', 'Voted', 'Ate']
      reportData.value = data.map(d => [d.date, d.meal_type, d.name, d.voted ? 'Yes' : 'No', d.ate ? 'Yes' : 'No'])
    } else if (key === 'meal_summary') {
      reportHeaders.value = ['Meal', 'Date', 'Votes', 'Served']
      reportData.value = data.map(d => [d.meal_type, d.date, d.votes, d.served])
    } else if (key === 'ratings_summary') {
      reportHeaders.value = ['Meal', 'Date', 'Count', 'Avg']
      reportData.value = data.map(d => [d.meal_type, d.date, d.count, d.avg_rating])
    }
  } catch (e) { toast.error('Error loading report') }
  finally { loading.value = false }
}

async function downloadPdf() {
  try {
    const { data } = await api.get('/api/reports/export-pdf', {
      params: {
        report_type: currentReportType.value,
        date_from: dateFrom.value,
        date_to: dateTo.value
      },
      responseType: 'blob'
    })
    const blob = new Blob([data], { type: 'application/pdf' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `${currentReportType.value}.pdf`
    link.click()
    URL.revokeObjectURL(link.href)
  } catch (e) { toast.error('Error downloading PDF') }
}

watch(currentPage, (v) => { if (v > totalPages.value) currentPage.value = totalPages.value })
</script>
