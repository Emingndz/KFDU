import { describe, expect, it } from 'vitest'
import { activityActionText } from './activity'
import type { ActivityOut } from '@/types'

function makeActivity(overrides: Partial<ActivityOut>): ActivityOut {
  return {
    id: 1,
    card_type: 'rating',
    actor: { id: 1, username: 'demo', display_name: null, avatar_url: null, bio: null },
    content: null,
    rating: null,
    review: null,
    status: null,
    list: null,
    created_at: '2026-09-27T00:00:00Z',
    likes_count: 0,
    liked_by_me: false,
    comments_count: 0,
    comments_preview: [],
    ...overrides,
  }
}

const movieContent = {
  id: 1,
  type: 'movie' as const,
  source: 'tmdb' as const,
  external_id: '27205',
  title: 'Inception',
  original_title: null,
  year: 2010,
  poster_url: null,
  genres: [],
  external_rating: null,
  creators: [],
}

describe('activityActionText', () => {
  it('puanlama için doğru metni üretir (film, tam hâliyle)', () => {
    const activity = makeActivity({ card_type: 'rating', content: movieContent })
    expect(activityActionText(activity)).toBe('bir filmi puanladı')
  })

  it('inceleme için kitaba özel metni üretir', () => {
    const activity = makeActivity({ card_type: 'review', content: { ...movieContent, type: 'book' } })
    expect(activityActionText(activity)).toBe('bir kitap hakkında inceleme yazdı')
  })

  it('durum güncellemesi için film/kitap ayrımı yapar', () => {
    const movieActivity = makeActivity({ card_type: 'status', status: 'completed', content: movieContent })
    expect(activityActionText(movieActivity)).toBe('izledi')

    const bookActivity = makeActivity({ card_type: 'status', status: 'completed', content: { ...movieContent, type: 'book' } })
    expect(activityActionText(bookActivity)).toBe('okudu')
  })

  it('listeye ekleme ve liste oluşturma için doğru metni üretir', () => {
    expect(activityActionText(makeActivity({ card_type: 'list_add', list: { id: 1, title: 'Favorilerim', item_count: 3, cover_urls: [] } }))).toBe(
      '"Favorilerim" listesine ekledi',
    )
    expect(activityActionText(makeActivity({ card_type: 'list_create' }))).toBe('yeni bir liste oluşturdu')
  })
})
