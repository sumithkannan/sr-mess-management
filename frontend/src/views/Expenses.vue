<template>
  <div class="space-y-4">
    <div class="flex justify-between items-center">
      <h2 class="font-semibold">Expenses</h2>
      <button @click="showForm = !showForm" class="text-sm bg-blue-600 text-white px-3 py-1.5 rounded">
        {{ showForm ? 'Cancel' : '+ Add' }}
      </button>
    </div>

    <div v-if="showForm" class="bg-white border rounded-lg p-4 space-y-3">
      <input v-model="form.description" placeholder="Description" class="w-full border rounded px-3 py-2 text-sm" />
      <input v-model="form.amount" type="number" step="0.01" placeholder="Amount" class="w-full border rounded px-3 py-2 text-sm" />
      <select v-model="form.category" class="w-full border rounded px-3 py-2 text-sm">
        <option value="">Category</option>
        <option>Grocery</option><option>Utility</option><option>Maintenance</option><option>Labor</option><option>Other</option>
      </select>
      <input type="date" v-model="form.expense_date" class="w-full border rounded px-3 py-2 text-sm" />
      <button @click="addExpense" class="bg-green-600 text-white px-4 py-2 rounded text-sm">Save</button>
    </div>

    <div class="flex gap-2">
      <select v-model="month" class="border rounded px-3 py-2 text-sm">
        <option v-for="(m, i) in months" :key="i" :value="i+1">{{ m }}</option>
      </select>
      <select v-model="year" class="border rounded px-3 py-2 text-sm">
        <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
      </select>
      <button @click="loadExpenses" class="bg-blue-600 text-white px-3 py-2 rounded text-sm">Load</button>
    </div>

    <div v-if="summary" class="bg-white border rounded-lg p-4 text-sm space-y-1">
      <p class="font-medium">Summary</p>
      <p>Total: Rs. {{ summary.total_expenses }}</p>
      <p>Entries: {{ summary.total_entries }}</p>
    </div>

    <div v-for="e in expenses" :key="e.id" class="bg-white border rounded-lg p-3 flex justify-between items-center text-sm">
      <div>
        <p class="font-medium">{{ e.description }}</p>
        <p class="text-xs text-gray-500">{{ e.category }} - {{ e.expense_date }}</p>
      </div>
      <span class="font-semibold text-blue-700">Rs. {{ e.amount }}</span>
    </div>
    <div v-if="expenses.length === 0" class="text-center py-8 text-gray-400">No expenses for this month</div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../api'

const dt = new Date()
const month = ref(dt.getMonth() + 1)
const year = ref(dt.getFullYear())
const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
const years = [dt.getFullYear() - 1, dt.getFullYear(), dt.getFullYear() + 1]
const expenses = ref([])
const summary = ref(null)
const showForm = ref(false)
const form = ref({ description: '', amount: '', category: '', expense_date: new Date().toISOString().split('T')[0] })

async function loadExpenses() {
  const [e, s] = await Promise.all([
    api.get('/api/expenses', { params: { month: month.value, year: year.value } }),
    api.get('/api/expenses/monthly-summary', { params: { month: month.value, year: year.value } })
  ])
  expenses.value = e.data
  summary.value = s.data
}

async function addExpense() {
  try {
    await api.post('/api/expenses', {
      description: form.value.description,
      amount: parseFloat(form.value.amount),
      category: form.value.category,
      expense_date: form.value.expense_date
    })
    loadExpenses(); showForm.value = false
    form.value = { description: '', amount: '', category: '', expense_date: new Date().toISOString().split('T')[0] }
  } catch (e) { alert(e.response?.data?.detail || 'Error') }
}
</script>
