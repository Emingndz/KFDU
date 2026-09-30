import type { NotificationOut } from '@/types'
import { contentPath } from './content'

export function notificationText(notification: NotificationOut): string {
  const name = notification.actor.display_name || notification.actor.username
  switch (notification.type) {
    case 'follow':
      return `${name} seni takip etmeye başladı`
    case 'like':
      return `${name} aktiviteni beğendi`
    case 'comment':
      return `${name} aktivitene yorum yaptı: "${notification.comment_excerpt ?? ''}"`
    default:
      return `${name} bir işlem yaptı`
  }
}

export function notificationPath(notification: NotificationOut): string {
  if (notification.type === 'follow') return `/u/${notification.actor.username}`
  if (notification.content) return contentPath(notification.content.type, notification.content.external_id)
  return `/u/${notification.actor.username}`
}
