import type { CatalogContentType } from '@/api/catalog'
import type { LibraryStatus } from '@/types'

const TYPE_LABELS: Record<CatalogContentType, string> = { movie: 'Film', tv: 'Dizi', book: 'Kitap' }
const TYPE_PATH_SEGMENTS: Record<CatalogContentType, string> = { movie: 'film', tv: 'dizi', book: 'kitap' }

export function typeLabel(type: CatalogContentType): string {
  return TYPE_LABELS[type]
}

export function contentPath(type: CatalogContentType, id: string | number): string {
  return `/${TYPE_PATH_SEGMENTS[type]}/${id}`
}

export function contentKey(type: CatalogContentType, id: string | number): string {
  return `${type}:${id}`
}

const STATUS_LABELS: Record<CatalogContentType, Record<LibraryStatus, string>> = {
  movie: { completed: 'İzledim', in_progress: 'İzliyorum', planned: 'İzleyeceğim', dropped: 'Yarım bıraktım' },
  tv: { completed: 'İzledim', in_progress: 'İzliyorum', planned: 'İzleyeceğim', dropped: 'Yarım bıraktım' },
  book: { completed: 'Okudum', in_progress: 'Okuyorum', planned: 'Okuyacağım', dropped: 'Yarım bıraktım' },
}

export function statusLabel(status: LibraryStatus, type: CatalogContentType): string {
  return STATUS_LABELS[type][status]
}

export function statusOptions(type: CatalogContentType): { value: LibraryStatus; label: string }[] {
  const labels = STATUS_LABELS[type]
  return (Object.keys(labels) as LibraryStatus[]).map((value) => ({ value, label: labels[value] }))
}
