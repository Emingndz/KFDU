import { useRouter } from 'vue-router'
import { useMarkNotificationRead } from '@/api/social'
import { notificationPath } from '@/utils/notifications'
import type { NotificationOut } from '@/types'

export function useNotificationClick() {
  const router = useRouter()
  const markRead = useMarkNotificationRead()

  function open(notification: NotificationOut) {
    if (!notification.is_read) markRead.mutate(notification.id)
    void router.push(notificationPath(notification))
  }

  return { open }
}
