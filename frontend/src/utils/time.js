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

// Milliseconds -> compact countdown: "2d 3h 15m", "3h 15m 20s", "15m 20s", "9s".
export function formatCountdown(ms) {
  const total = Math.max(0, Math.ceil(ms / 1000))
  const days = Math.floor(total / 86400)
  const hours = Math.floor((total % 86400) / 3600)
  const minutes = Math.floor((total % 3600) / 60)
  const seconds = total % 60
  if (days > 0) return `${days}d ${hours}h ${minutes}m`
  if (hours > 0) return `${hours}h ${minutes}m ${seconds}s`
  if (minutes > 0) return `${minutes}m ${seconds}s`
  return `${seconds}s`
}

// Pick the meal that is relevant right now: the first one whose attendance
// window (including its buffer) contains `nowMs`, otherwise the next window to
// open, otherwise the meal whose window ended most recently. `mealTypes` must
// be in display order, which also breaks ties.
export function pickCurrentMealType(mealTypes, dateStr, nowMs = Date.now()) {
  const windowOf = mt => (
    mt && mt.start_time && mt.end_time && mt.attendance_buffer_hours != null
      ? mealWindow(dateStr, mt.start_time, mt.end_time, mt.attendance_buffer_hours)
      : null
  )
  const windows = mealTypes.map(mt => ({ mt, w: windowOf(mt) }))

  const open = windows.find(x => x.w && nowMs >= x.w.start.getTime() && nowMs < x.w.end.getTime())
  if (open) return String(open.mt.id)

  const upcoming = windows
    .filter(x => x.w && x.w.start.getTime() > nowMs)
    .sort((a, b) => a.w.start - b.w.start)
  if (upcoming.length) return String(upcoming[0].mt.id)

  // Every window is in the past: stay on the last meal served, not the first.
  let lastEnded = null
  for (const x of windows) {
    if (!x.w) continue
    if (!lastEnded || x.w.end.getTime() > lastEnded.w.end.getTime()) lastEnded = x
  }
  if (lastEnded) return String(lastEnded.mt.id)

  return mealTypes.length ? String(mealTypes[0].id) : ''
}
