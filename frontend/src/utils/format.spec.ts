import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { formatCount, formatDate, formatPages, formatRating, formatRuntime, relativeTime } from './format'

describe('relativeTime', () => {
  const NOW = new Date('2026-09-26T12:00:00.000Z')

  beforeEach(() => {
    vi.useFakeTimers()
    vi.setSystemTime(NOW)
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('çok yakın zamanı "az önce" olarak gösterir', () => {
    expect(relativeTime(new Date(NOW.getTime() - 10_000).toISOString())).toBe('az önce')
  })

  it('dakikaları göreli olarak gösterir', () => {
    expect(relativeTime(new Date(NOW.getTime() - 3 * 60_000).toISOString())).toContain('dakika')
  })

  it('bir gün önceyi "dün" olarak gösterir', () => {
    expect(relativeTime(new Date(NOW.getTime() - 24 * 60 * 60_000).toISOString())).toBe('dün')
  })

  it('haftaları göreli olarak gösterir', () => {
    expect(relativeTime(new Date(NOW.getTime() - 21 * 24 * 60 * 60_000).toISOString())).toContain('hafta')
  })

  it('30 günden eski tarihi mutlak tarihe çevirir', () => {
    const old = new Date(NOW.getTime() - 45 * 24 * 60 * 60_000).toISOString()
    expect(relativeTime(old)).toBe(formatDate(old))
  })
})

describe('formatRuntime', () => {
  it('yalnızca dakikayı doğru biçimlendirir', () => {
    expect(formatRuntime(45)).toBe('45 dk')
  })

  it('tam saatleri doğru biçimlendirir', () => {
    expect(formatRuntime(120)).toBe('2 sa')
  })

  it('saat ve dakikayı birlikte biçimlendirir', () => {
    expect(formatRuntime(150)).toBe('2 sa 30 dk')
  })
})

describe('formatPages', () => {
  it('sayfa sayısını biçimlendirir', () => {
    expect(formatPages(412)).toBe('412 sayfa')
  })
})

describe('formatRating', () => {
  it('puanı x/10 biçiminde gösterir', () => {
    expect(formatRating(8)).toBe('8/10')
  })
})

describe('formatCount', () => {
  it('1000 altını olduğu gibi gösterir', () => {
    expect(formatCount(842)).toBe('842')
  })

  it('bini "B" ile kısaltır', () => {
    expect(formatCount(1234)).toBe('1,2 B')
  })

  it('milyonu "M" ile kısaltır', () => {
    expect(formatCount(2_500_000)).toBe('2,5 M')
  })
})
