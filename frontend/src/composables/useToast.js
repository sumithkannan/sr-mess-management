import { ref } from 'vue'

const toasts = ref([])
let id = 0

export function useToast() {
  function add(message, type = 'info', duration = 3000) {
    const toast = { id: id++, message, type }
    toasts.value.push(toast)
    setTimeout(() => remove(toast.id), duration)
  }
  function success(message, duration = 3000) { add(message, 'success', duration) }
  function warning(message, duration = 4000) { add(message, 'warning', duration) }
  function error(message, duration = 5000) { add(message, 'error', duration) }
  function remove(toastId) {
    toasts.value = toasts.value.filter(t => t.id !== toastId)
  }
  return { toasts, add, success, warning, error, remove }
}
