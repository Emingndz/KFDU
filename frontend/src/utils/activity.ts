import type { ActivityOut } from '@/types'
import type { CatalogContentType } from '@/api/catalog'

const TYPE_NOUN: Record<CatalogContentType, string> = { movie: 'film', tv: 'dizi', book: 'kitap' }
const TYPE_NOUN_ACC: Record<CatalogContentType, string> = { movie: 'filmi', tv: 'diziyi', book: 'kitabı' }

const STATUS_VERBS: Record<CatalogContentType, Record<string, string>> = {
  movie: { completed: 'izledi', in_progress: 'izlemeye başladı', planned: 'izleneceklerine ekledi', dropped: 'yarım bıraktı' },
  tv: { completed: 'izledi', in_progress: 'izlemeye başladı', planned: 'izleneceklerine ekledi', dropped: 'yarım bıraktı' },
  book: { completed: 'okudu', in_progress: 'okumaya başladı', planned: 'okunacaklarına ekledi', dropped: 'yarım bıraktı' },
}

export function activityActionText(activity: ActivityOut): string {
  const type = activity.content?.type
  switch (activity.card_type) {
    case 'rating':
      return `bir ${type ? TYPE_NOUN_ACC[type] : 'içeriği'} puanladı`
    case 'review':
      return `bir ${type ? TYPE_NOUN[type] : 'içerik'} hakkında inceleme yazdı`
    case 'status':
      return (type && activity.status && STATUS_VERBS[type][activity.status]) || 'durumunu güncelledi'
    case 'list_add':
      return `"${activity.list?.title ?? ''}" listesine ekledi`
    case 'list_create':
      return 'yeni bir liste oluşturdu'
    default:
      return ''
  }
}
