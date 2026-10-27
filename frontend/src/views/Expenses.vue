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
        <option>Grocery</option><option>Utility</option><option>Maintenance</option><option>Labour</option><option>Other</option>
      </select>
      <input type="date" v-model="form.expense_date" class="w-full border rounded px-3 py-2 text-sm" />
      
      <div class="space-y-2">
        <p class="text-sm font-medium text-gray-700">Bill Image (optional, max 2MB)</p>
        <button @click="showImageOptions = !showImageOptions" class="w-full bg-gray-100 text-gray-700 px-3 py-2 rounded text-sm hover:bg-gray-200 flex items-center justify-center gap-2">
          📷 Attach Bill Image
        </button>
        <div v-if="showImageOptions && !imagePreview" class="flex gap-2">
          <button @click="openCamera(); showImageOptions = false" class="flex-1 bg-blue-50 text-blue-700 px-3 py-2 rounded text-sm hover:bg-blue-100">Take Photo</button>
          <button @click="openGallery(); showImageOptions = false" class="flex-1 bg-blue-50 text-blue-700 px-3 py-2 rounded text-sm hover:bg-blue-100">Upload from Gallery</button>
        </div>
        <input ref="cameraInput" type="file" accept="image/*" capture="environment" @change="handleImageSelect" class="hidden" />
        <input ref="galleryInput" type="file" accept="image/*" @change="handleImageSelect" class="hidden" />
        <div v-if="imagePreview" class="relative">
          <img :src="imagePreview" class="w-full h-32 object-cover rounded border" />
          <button @click="clearImage" class="absolute top-1 right-1 bg-red-500 text-white rounded-full w-6 h-6 text-xs">×</button>
          <p class="text-xs text-gray-500 mt-1">{{ imageSizeText }}</p>
        </div>
        <p v-if="compressing" class="text-xs text-yellow-600">Compressing image...</p>
      </div>
      
      <button @click="addExpense" :disabled="compressing" class="bg-green-600 text-white px-4 py-2 rounded text-sm disabled:opacity-50">Save</button>
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

const cameraInput = ref(null)
const galleryInput = ref(null)
const imageFile = ref(null)
const imagePreview = ref('')
const imageSizeText = ref('')
const compressing = ref(false)
const showImageOptions = ref(false)

function openCamera() { cameraInput.value?.click() }
function openGallery() { galleryInput.value?.click() }

async function compressImage(file) {
  compressing.value = true
  try {
    const maxSize = 2 * 1024 * 1024
    if (file.size <= maxSize) {
      imageFile.value = file
      imagePreview.value = URL.createObjectURL(file)
      imageSizeText.value = `Original: ${(file.size/1024).toFixed(0)}KB`
      compressing.value = false
      return
    }
    
    alert('Image is compressing...')
    
    return new Promise((resolve) => {
      const img = new Image()
      img.onload = () => {
        const canvas = document.createElement('canvas')
        let width = img.width
        let height = img.height
        const maxDim = 1024
        if (width > maxDim || height > maxDim) {
          const ratio = Math.min(maxDim / width, maxDim / height)
          width = Math.round(width * ratio)
          height = Math.round(height * ratio)
        }
        canvas.width = width
        canvas.height = height
        const ctx = canvas.getContext('2d')
        ctx.drawImage(img, 0, 0, width, height)
        
        const compress = (quality) => {
          canvas.toBlob((blob) => {
            if (!blob) { resolve(); return }
            if (blob.size > maxSize && quality > 0.3) {
              compress(quality - 0.1)
            } else {
              const compressedFile = new File([blob], 'bill.jpg', { type: 'image/jpeg' })
              imageFile.value = compressedFile
              imagePreview.value = URL.createObjectURL(compressedFile)
              imageSizeText.value = `Compressed: ${(blob.size/1024).toFixed(0)}KB (quality: ${(quality*100).toFixed(0)}%)`
              compressing.value = false
              resolve()
            }
          }, 'image/jpeg', quality)
        }
        compress(0.8)
      }
      img.src = URL.createObjectURL(file)
    })
  } catch (e) {
    alert('Failed to compress image')
    compressing.value = false
  }
}

async function handleImageSelect(e) {
  const file = e.target.files[0]
  if (!file) return
  await compressImage(file)
  e.target.value = ''
}

function clearImage() {
  imageFile.value = null
  imagePreview.value = ''
  imageSizeText.value = ''
  showImageOptions.value = false
}

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
    if (imageFile.value) {
      const fd = new FormData()
      fd.append('description', form.value.description)
      fd.append('amount', form.value.amount)
      fd.append('category', form.value.category)
      fd.append('expense_date', form.value.expense_date)
      fd.append('bill', imageFile.value)
      await api.post('/api/expenses/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    } else {
      await api.post('/api/expenses', {
        description: form.value.description,
        amount: parseFloat(form.value.amount),
        category: form.value.category,
        expense_date: form.value.expense_date
      })
    }
    loadExpenses(); showForm.value = false
    form.value = { description: '', amount: '', category: '', expense_date: new Date().toISOString().split('T')[0] }
    clearImage()
    showImageOptions.value = false
  } catch (e) { alert(e.response?.data?.detail || 'Error') }
}
</script>
