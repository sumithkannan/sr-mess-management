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

    <div v-if="reportData.length && !loading" class="bg-white rounded-lg border overflow-x-auto">
      <table class="w-full text-sm">
        <thead class="bg-gray-50">
          <tr>
            <th v-for="h in reportHeaders" :key="h" class="px-3 py-2.5 text-left font-medium">{{ h }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, i) in reportData" :key="i" class="border-t hover:bg-gray-50">
            <td v-for="(val, j) in row" :key="j" class="px-3 py-2">{{ val }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="noData && !loading" class="text-center py-8 text-gray-400">No data for selected period</div>

    <button v-if="reportData.length && !loading" @click="downloadPdf"
      class="bg-red-600 text-white px-4 py-2.5 rounded text-sm w-full hover:bg-red-700">
      Download PDF
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../api'

const dateFrom = ref(new Date(Date.now() - 7*86400000).toISOString().split('T')[0])
const dateTo = ref(new Date().toISOString().split('T')[0])
const activeReport = ref('')
const reportData = ref([])
const reportHeaders = ref([])
const loading = ref(false)
const noData = ref(false)
const currentReportType = ref('')

const reportTypes = [
  { key: 'vote_vs_attendance', label: 'Vote vs Eat' },
  { key: 'meal_summary', label: 'Meal Summary' },
  { key: 'ratings_summary', label: 'Ratings' },
]

async function loadReport(key) {
  activeReport.value = key
  currentReportType.value = key
  loading.value = true; noData.value = false
  try {
    const { data } = await api.get(`/api/reports/${key.replace(/_/g, '-')}`, {
      params: { date_from: dateFrom.value, date_to: dateTo.value }
    })
    if (!data.length) { noData.value = true; reportData.value = []; return }
    if (key === 'vote_vs_attendance') {
      reportHeaders.value = ['Name', 'Voted', 'Ate']
      reportData.value = data.map(d => [d.name, d.voted ? 'Yes' : 'No', d.ate ? 'Yes' : 'No'])
    } else if (key === 'meal_summary') {
      reportHeaders.value = ['Meal', 'Date', 'Votes', 'Served']
      reportData.value = data.map(d => [d.meal_type, d.date, d.votes, d.served])
    } else if (key === 'ratings_summary') {
      reportHeaders.value = ['Meal', 'Date', 'Count', 'Avg']
      reportData.value = data.map(d => [d.meal_type, d.date, d.count, d.avg_rating])
    }
  } catch (e) { alert('Error loading report') }
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
  } catch (e) { alert('Error downloading PDF') }
}
</script>
