// Time helpers that keep the UI in sync with the backend's business timezone.
// The backend interprets meal times in `settings.TIMEZONE` (Asia/Kolkata), so
// the browser must not use its own timezone to decide whether a window is open.
// India has no DST, so a fixed offset is safe.

export const APP_TIMEZONE = 'Asia/Kolkata'
const TZ_OFFSET_MS = 5.5 * 60 * 60 * 1000
const DAY_MS = 24 * 60 * 60 * 1000

// Today's date (YYYY-MM-DD) in the app timezone, not the UTC date.
export function todayStr(now = new Date()) {
  return new Date(now.getTime() + TZ_OFFSET_MS).toISOString().slice(0, 10)
}

// Epoch milliseconds for a wall-clock date/time in the app timezone.
export function zonedTimestamp(dateStr, hours = 0, minutes = 0) {
  const [y, m, d] = dateStr.split('-').map(Number)
  return Date.UTC(y, m - 1, d, hours, minutes) - TZ_OFFSET_MS
}

// Window around a meal, as Date objects. Handles meals crossing midnight.
export function mealWindow(dateStr, startTime, endTime, bufferHours = 1) {
  const [sh, sm] = startTime.split(':').map(Number)
  const [eh, em] = endTime.split(':').map(Number)
  const buffer = bufferHours * 60 * 60 * 1000
  const start = zonedTimestamp(dateStr, sh, sm) - buffer
  let end = zonedTimestamp(dateStr, eh, em) + buffer
  if (end <= start) end += DAY_MS
  return { start: new Date(start), end: new Date(end) }
}

const DAY_MINUTES = 24 * 60

// "HH:MM" -> minutes after midnight, or null when the value is empty/invalid.
export function clockMinutes(time) {
  if (!time) return null
  const [h, m] = time.split(':').map(Number)
  if (!Number.isFinite(h) || !Number.isFinite(m)) return null
  return h * 60 + m
}

// Minutes after midnight -> "7:00 PM".
export function formatClock(minutes) {
  const normalized = ((minutes % DAY_MINUTES) + DAY_MINUTES) % DAY_MINUTES
  const h24 = Math.floor(normalized / 60)
  const mm = String(normalized % 60).padStart(2, '0')
  const suffix = h24 < 12 ? 'AM' : 'PM'
  const h12 = h24 % 12 === 0 ? 12 : h24 % 12
  return `${h12}:${mm} ${suffix}`
}

// Minutes relative to the meal's own date -> "7:00 PM previous day".
export function describeClockOffset(minutes) {
  const day = Math.floor(minutes / DAY_MINUTES)
  const clock = formatClock(minutes)
  if (day === 0) return clock
  if (day === -1) return `${clock} previous day`
  if (day === 1) return `${clock} next day`
  return day < 0 ? `${clock} ${-day} days before` : `${clock} ${day} days after`
}
