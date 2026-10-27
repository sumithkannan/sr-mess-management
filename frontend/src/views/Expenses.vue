<template>
  <div class="space-y-4">
    <div class="flex justify-between items-center">
      <h2 class="font-semibold">Expenses</h2>
      <button @click="toggleForm" class="text-sm bg-blue-600 text-white px-3 py-1.5 rounded">
        {{ showForm ? 'Cancel' : '+ Add' }}
      </button>
    </div>

    <div v-if="showForm" class="bg-white border rounded-lg p-4 space-y-3">
      <p class="text-sm font-medium text-gray-700">{{ editingId ? 'Edit Expense' : 'New Expense' }}</p>
      <input v-model="form.description" placeholder="Description" class="w-full border rounded px-3 py-2 text-sm" />
      <input v-model="form.amount" type="number" step="0.01" placeholder="Amount" class="w-full border rounded px-3 py-2 text-sm" />
      <select v-model="form.category" class="w-full border rounded px-3 py-2 text-sm">
        <option value="">Category</option>
        <option>Grocery</option><option>Utility</option><option>Maintenance</option><option>Labour</option><option>Other</option>
      </select>
      <input type="date" v-model="form.expense_date" class="w-full border rounded px-3 py-2 text-sm" />

      <div class="space-y-2">
        <p class="text-sm font-medium text-gray-700">Bill Image (optional, saved under 2MB)</p>
        <button v-if="!displayedPreview" @click="showImageOptions = !showImageOptions" class="w-full bg-gray-100 text-gray-700 px-3 py-2 rounded text-sm hover:bg-gray-200 flex items-center justify-center gap-2">
          📎 Attach Bill Image
        </button>
        <div v-if="showImageOptions && !displayedPreview" class="flex gap-2">
          <button @click="openCamera(); showImageOptions = false" class="flex-1 bg-blue-50 text-blue-700 px-3 py-2 rounded text-sm hover:bg-blue-100">Take Photo</button>
          <button @click="openGallery(); showImageOptions = false" class="flex-1 bg-blue-50 text-blue-700 px-3 py-2 rounded text-sm hover:bg-blue-100">Upload from Gallery</button>
        </div>
        <input ref="cameraInput" type="file" accept="image/*" capture="environment" @change="handleImageSelect" class="hidden" />
        <input ref="galleryInput" type="file" accept="image/*" @change="handleImageSelect" class="hidden" />
        <div v-if="displayedPreview" class="relative">
          <img :src="displayedPreview" class="w-full h-32 object-cover rounded border" />
          <button @click="removePreview" class="absolute top-1 right-1 bg-red-500 text-white rounded-full w-6 h-6 text-xs">✕</button>
          <p class="text-xs text-gray-500 mt-1">{{ imageSizeText || (imageFile ? '' : 'Existing bill image') }}</p>
        </div>
        <p v-if="compressing" class="text-xs text-yellow-600">Compressing image...</p>
      </div>

      <div class="flex gap-2">
        <button @click="saveExpense" :disabled="compressing" class="bg-green-600 text-white px-4 py-2 rounded text-sm disabled:opacity-50">
          {{ editingId ? 'Update' : 'Save' }}
        </button>
        <button @click="cancelForm" class="bg-gray-100 text-gray-700 px-4 py-2 rounded text-sm hover:bg-gray-200">Cancel</button>
      </div>
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

    <div v-if="summary" class="bg-white border rounded-lg px-4 py-3 text-sm flex justify-between items-center">
      <div>
        <p class="text-xs text-gray-500">Monthly expenses</p>
        <p class="font-semibold text-blue-700">Rs. {{ summary.total_expenses }}</p>
      </div>
      <p class="text-xs text-gray-500">{{ summary.total_entries }} entries</p>
    </div>

    <div v-if="expenses.length" class="bg-white border rounded-lg overflow-hidden">
      <div class="grid grid-cols-[1fr_auto] gap-3 px-4 py-2 bg-gray-50 text-[11px] uppercase tracking-wide text-gray-500">
        <span>Expense</span>
        <span>Amount</span>
      </div>
      <button
        v-for="e in expenses"
        :key="e.id"
        @click="selectExpense(e)"
        class="w-full grid grid-cols-[1fr_auto] gap-3 items-center px-4 py-3 text-left border-t hover:bg-gray-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-blue-500"
      >
        <span class="min-w-0">
          <span class="block font-medium text-sm break-words">{{ e.description }}</span>
          <span class="block text-xs text-gray-500 mt-0.5">{{ e.expense_date }} <span class="mx-1">·</span> {{ e.category }}</span>
        </span>
        <span class="font-semibold text-sm text-gray-800 whitespace-nowrap">Rs. {{ e.amount }}</span>
      </button>
    </div>
    <div v-if="expenses.length === 0" class="text-center py-8 text-gray-400">No expenses for this month</div>

    <Teleport to="body">
      <div v-if="selectedExpense" class="fixed inset-0 z-[9997] bg-black/50 flex items-center justify-center p-4" @click.self="selectedExpense = null">
        <section class="bg-white rounded-xl shadow-xl w-full max-w-sm p-5 space-y-4" role="dialog" aria-modal="true" aria-labelledby="expense-detail-title">
          <div class="flex justify-between items-start gap-3">
            <div class="min-w-0">
              <p class="text-xs text-gray-500">{{ selectedExpense.expense_date }} <span class="mx-1">·</span> {{ selectedExpense.category }}</p>
              <h3 id="expense-detail-title" class="font-semibold text-lg break-words mt-1">{{ selectedExpense.description }}</h3>
            </div>
            <button @click="selectedExpense = null" aria-label="Close expense details" class="text-gray-500 hover:text-gray-800">✕</button>
          </div>
          <p class="text-2xl font-semibold text-blue-700">Rs. {{ selectedExpense.amount }}</p>
          <button v-if="selectedExpense.bill_image" @click="viewBill(selectedExpense)" class="text-sm text-blue-600 hover:text-blue-800">
            {{ billUrls[selectedExpense.id] ? 'View bill image' : 'Open bill image' }}
          </button>
          <p v-else class="text-sm text-gray-500">No bill image attached</p>
          <div class="flex gap-2 pt-2 border-t">
            <button @click="startEdit(selectedExpense)" class="flex-1 bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-700">Edit</button>
            <button @click="deleteExpense(selectedExpense)" class="flex-1 bg-red-50 text-red-700 px-4 py-2 rounded text-sm hover:bg-red-100">Delete</button>
          </div>
        </section>
      </div>
      <div v-if="viewerUrl" class="fixed inset-0 z-[9998] bg-black/80 flex items-center justify-center p-4" @click="viewerUrl = ''">
        <div class="relative max-h-full max-w-full">
          <img :src="viewerUrl" class="max-h-[85vh] max-w-full rounded" />
          <button @click="viewerUrl = ''" class="absolute -top-3 -right-3 bg-white text-gray-700 rounded-full w-8 h-8 text-sm shadow">✕</button>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import api from '../api'
import { useToast } from '../composables/useToast'

const toast = useToast()

const dt = new Date()
const month = ref(dt.getMonth() + 1)
const year = ref(dt.getFullYear())
const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
const years = [dt.getFullYear() - 1, dt.getFullYear(), dt.getFullYear() + 1]
const expenses = ref([])
const summary = ref(null)
const showForm = ref(false)
const editingId = ref(null)
const selectedExpense = ref(null)
const form = ref({ description: '', amount: '', category: '', expense_date: new Date().toISOString().split('T')[0] })

const cameraInput = ref(null)
const galleryInput = ref(null)
const imageFile = ref(null)
const imagePreview = ref('')
const imageSizeText = ref('')
const compressing = ref(false)
const showImageOptions = ref(false)

const existingBillPreview = ref('')
const removeBill = ref(false)
const billUrls = ref({})
const viewerUrl = ref('')

const displayedPreview = computed(() => {
  if (imagePreview.value) return imagePreview.value
  if (removeBill.value) return ''
  return existingBillPreview.value
})

function openCamera() { cameraInput.value?.click() }
function openGallery() { galleryInput.value?.click() }

function resetImageState() {
  imageFile.value = null
  imagePreview.value = ''
  imageSizeText.value = ''
  existingBillPreview.value = ''
  removeBill.value = false
  showImageOptions.value = false
  compressing.value = false
}

function resetForm() {
  showForm.value = false
  editingId.value = null
  form.value = { description: '', amount: '', category: '', expense_date: new Date().toISOString().split('T')[0] }
  resetImageState()
}

function toggleForm() {
  if (showForm.value) resetForm()
  else {
    editingId.value = null
    form.value = { description: '', amount: '', category: '', expense_date: new Date().toISOString().split('T')[0] }
    resetImageState()
    showForm.value = true
  }
}

function cancelForm() {
  resetForm()
}

function removePreview() {
  if (imagePreview.value) {
    URL.revokeObjectURL(imagePreview.value)
  }
  imageFile.value = null
  imagePreview.value = ''
  imageSizeText.value = ''
  if (existingBillPreview.value) {
    removeBill.value = true
  }
  showImageOptions.value = false
}

const CLIENT_MAX_SIZE = 2 * 1024 * 1024
const SERVER_MAX_SIZE = 10 * 1024 * 1024

async function isHeicFile(file) {
  try {
    const head = new Uint8Array(await file.slice(0, 12).arrayBuffer())
    if (head.length < 12) return false
    const brand = String.fromCharCode(...head.slice(4, 12)).toLowerCase()
    return /heic|heix|hevc|hevx|mif1|msf1/.test(brand)
  } catch (e) {
    return false
  }
}

function useOriginal(file, note) {
  imageFile.value = file
  imagePreview.value = URL.createObjectURL(file)
  imageSizeText.value = note || `Original: ${(file.size / 1024).toFixed(0)}KB`
}

async function compressWithBitmap(file) {
  if (typeof createImageBitmap !== 'function') return null
  let bitmap
  try {
    bitmap = await createImageBitmap(file)
  } catch (e) {
    console.warn('[Compress] createImageBitmap failed', e)
    return null
  }
  try {
    for (const maxDim of [1024, 800, 640, 512, 400]) {
      const ratio = Math.min(1, maxDim / bitmap.width, maxDim / bitmap.height)
      const w = Math.max(1, Math.round(bitmap.width * ratio))
      const h = Math.max(1, Math.round(bitmap.height * ratio))
      const canvas = document.createElement('canvas')
      canvas.width = w
      canvas.height = h
      const ctx = canvas.getContext('2d')
      if (!ctx) continue
      ctx.drawImage(bitmap, 0, 0, w, h)
      for (let q = 0.8; q >= 0.3; q -= 0.1) {
        const blob = await new Promise(res => canvas.toBlob(res, 'image/jpeg', q))
        if (!blob) break
        if (blob.size <= CLIENT_MAX_SIZE) return blob
      }
    }
  } catch (e) {
    console.warn('[Compress] bitmap pipeline failed', e)
  } finally {
    if (bitmap.close) bitmap.close()
  }
  return null
}

function compressWithImageElement(file) {
  return new Promise(resolve => {
    const img = new Image()
    img.onload = () => {
      try {
        const attempt = (maxDim) => {
          const ratio = Math.min(1, maxDim / img.width, maxDim / img.height)
          const w = Math.max(1, Math.round(img.width * ratio))
          const h = Math.max(1, Math.round(img.height * ratio))
          const canvas = document.createElement('canvas')
          canvas.width = w
          canvas.height = h
          const ctx = canvas.getContext('2d')
          if (!ctx) return resolve(null)
          ctx.drawImage(img, 0, 0, w, h)

          const tryQuality = (q) => {
            canvas.toBlob(blob => {
              if (!blob) {
                return maxDim > 400 ? attempt(Math.round(maxDim / 1.25)) : resolve(null)
              }
              if (blob.size <= CLIENT_MAX_SIZE) return resolve(blob)
              if (q > 0.3) return tryQuality(q - 0.1)
              if (maxDim > 400) return attempt(Math.round(maxDim / 1.25))
              resolve(null)
            }, 'image/jpeg', q)
          }
          tryQuality(0.8)
        }
        attempt(1024)
      } catch (e) {
        console.warn('[Compress] image pipeline failed', e)
        resolve(null)
      }
    }
    img.onerror = (e) => {
      console.warn('[Compress] image decode failed', e)
      resolve(null)
    }
    img.src = URL.createObjectURL(file)
  })
}

async function compressImage(file) {
  compressing.value = true
  try {
    // HEIC/HEIF cannot be decoded by most browsers or by the server (no pillow-heif)
    if (await isHeicFile(file)) {
      toast.error('HEIC photos are not supported. On iPhone use Settings > Camera > Formats > Most Compatible, or choose a JPG from gallery.')
      imageFile.value = null
      imagePreview.value = ''
      imageSizeText.value = ''
      return
    }

    if (file.size <= CLIENT_MAX_SIZE) {
      useOriginal(file)
      return
    }

    toast.info('Image is compressing...')

    let blob = await compressWithBitmap(file)
    if (!blob) blob = await compressWithImageElement(file)

    if (blob) {
      const compressedFile = new File([blob], 'bill.jpg', { type: 'image/jpeg' })
      imageFile.value = compressedFile
      imagePreview.value = URL.createObjectURL(compressedFile)
      imageSizeText.value = `Compressed: ${(blob.size / 1024).toFixed(0)}KB`
      return
    }

    // Client compression unavailable: let the server compress it (it always
    // resizes/re-encodes and stores under 2MB).
    if (file.size <= SERVER_MAX_SIZE) {
      useOriginal(file, `${(file.size / 1024 / 1024).toFixed(1)}MB - will be compressed on upload`)
      return
    }

    toast.error(`Photo is too large (${(file.size / 1024 / 1024).toFixed(1)}MB). Please use an image under 10MB or lower your camera resolution.`)
    imageFile.value = null
    imagePreview.value = ''
    imageSizeText.value = ''
  } catch (e) {
    console.warn('[Compress] unexpected failure', e)
    if (file.size <= SERVER_MAX_SIZE) {
      useOriginal(file, `${(file.size / 1024 / 1024).toFixed(1)}MB - will be compressed on upload`)
    } else {
      toast.error('Could not process this photo. Please pick a smaller JPG/PNG.')
      imageFile.value = null
      imagePreview.value = ''
      imageSizeText.value = ''
    }
  } finally {
    compressing.value = false
  }
}

async function handleImageSelect(e) {
  const file = e.target.files[0]
  if (!file) return
  await compressImage(file)
  e.target.value = ''
}

function revokeBillUrls() {
  for (const url of Object.values(billUrls.value)) {
    URL.revokeObjectURL(url)
  }
  billUrls.value = {}
}

async function ensureBillUrl(e) {
  if (!e.bill_image) return ''
  if (billUrls.value[e.id]) return billUrls.value[e.id]
  try {
    const res = await api.get(`/api/expenses/${e.id}/bill`, { responseType: 'blob' })
    const url = URL.createObjectURL(res.data)
    billUrls.value[e.id] = url
    return url
  } catch (err) {
    toast.error(err.response?.data?.detail || 'Error loading bill image')
    return ''
  }
}

async function loadExpenses() {
  try {
    const [e, s] = await Promise.all([
      api.get('/api/expenses', { params: { month: month.value, year: year.value } }),
      api.get('/api/expenses/monthly-summary', { params: { month: month.value, year: year.value } })
    ])
    revokeBillUrls()
    expenses.value = e.data
    summary.value = s.data
  } catch (err) {
    toast.error(err.response?.data?.detail || 'Error loading expenses')
  }
}

async function startEdit(e) {
  selectedExpense.value = null
  editingId.value = e.id
  form.value = {
    description: e.description,
    amount: String(e.amount),
    category: e.category,
    expense_date: e.expense_date
  }
  resetImageState()
  existingBillPreview.value = await ensureBillUrl(e)
  showForm.value = true
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

async function selectExpense(e) {
  selectedExpense.value = e
  if (e.bill_image) await ensureBillUrl(e)
}

async function viewBill(e) {
  const url = await ensureBillUrl(e)
  if (url) viewerUrl.value = url
}

async function deleteExpense(e) {
  if (!confirm(`Delete expense "${e.description}"?`)) return
  try {
    await api.delete(`/api/expenses/${e.id}`)
    selectedExpense.value = null
    toast.success('Expense deleted')
    await loadExpenses()
  } catch (err) {
    toast.error(err.response?.data?.detail || 'Error deleting expense')
  }
}

async function saveExpense() {
  if (!form.value.description || !form.value.amount || !form.value.category || !form.value.expense_date) {
    toast.error('Please fill all fields')
    return
  }

  try {
    if (editingId.value) {
      if (imageFile.value || removeBill.value) {
        const fd = new FormData()
        fd.append('description', form.value.description)
        fd.append('amount', form.value.amount)
        fd.append('category', form.value.category)
        fd.append('expense_date', form.value.expense_date)
        if (imageFile.value) fd.append('bill', imageFile.value)
        fd.append('remove_bill', removeBill.value ? 'true' : 'false')
        await api.put(`/api/expenses/${editingId.value}/upload`, fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      } else {
        await api.put(`/api/expenses/${editingId.value}`, {
          description: form.value.description,
          amount: parseFloat(form.value.amount),
          category: form.value.category,
          expense_date: form.value.expense_date
        })
      }
      toast.success('Expense updated')
    } else {
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
      toast.success('Expense added')
    }
    resetForm()
    await loadExpenses()
  } catch (err) {
    toast.error(err.response?.data?.detail || 'Error saving expense')
  }
}

onMounted(loadExpenses)
onBeforeUnmount(revokeBillUrls)
</script>
