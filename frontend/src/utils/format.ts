const rtf = new Intl.RelativeTimeFormat('tr', { numeric: 'auto' })
const JUST_NOW_THRESHOLD_SECONDS = 45
const ABSOLUTE_THRESHOLD_DAYS = 30

export function formatDate(iso: string): string {
  return new Intl.DateTimeFormat('tr', { dateStyle: 'long' }).format(new Date(iso))
}

export function relativeTime(iso: string): string {
  const diffSeconds = Math.round((new Date(iso).getTime() - Date.now()) / 1000)

  if (Math.abs(diffSeconds) < JUST_NOW_THRESHOLD_SECONDS) return diffSeconds <= 0 ? 'az önce' : 'az sonra'

  const diffMinutes = Math.round(diffSeconds / 60)
  if (Math.abs(diffMinutes) < 60) return rtf.format(diffMinutes, 'minute')

  const diffHours = Math.round(diffMinutes / 60)
  if (Math.abs(diffHours) < 24) return rtf.format(diffHours, 'hour')

  const diffDays = Math.round(diffHours / 24)
  if (Math.abs(diffDays) < 7) return rtf.format(diffDays, 'day')
  if (Math.abs(diffDays) <= ABSOLUTE_THRESHOLD_DAYS) return rtf.format(Math.round(diffDays / 7), 'week')

  return formatDate(iso)
}

export function formatRuntime(minutes: number): string {
  const hours = Math.floor(minutes / 60)
  const remaining = minutes % 60
  if (hours === 0) return `${remaining} dk`
  if (remaining === 0) return `${hours} sa`
  return `${hours} sa ${remaining} dk`
}

export function formatPages(pages: number): string {
  return `${pages} sayfa`
}

export function formatRating(rating: number): string {
  return `${rating}/10`
}

export function formatCount(count: number): string {
  const abbreviate = (value: number) => (Math.round(value * 10) / 10).toLocaleString('tr-TR', { maximumFractionDigits: 1 })
  if (count < 1000) return String(count)
  if (count < 1_000_000) return `${abbreviate(count / 1000)} B`
  return `${abbreviate(count / 1_000_000)} M`
}
