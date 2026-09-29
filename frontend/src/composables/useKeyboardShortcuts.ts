import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useEventListener } from '@vueuse/core'
import { requestSearchFocus } from '@/composables/useSearchFocus'

function isEditableTarget(target: EventTarget | null): boolean {
  if (!(target instanceof HTMLElement)) return false
  return target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable
}

export function useKeyboardShortcuts() {
  const router = useRouter()
  const helpOpen = ref(false)

  let awaitingSecondKey = false
  let resetTimer: ReturnType<typeof setTimeout> | null = null

  function armGPrefix() {
    awaitingSecondKey = true
    if (resetTimer) clearTimeout(resetTimer)
    resetTimer = setTimeout(() => (awaitingSecondKey = false), 1000)
  }

  function focusOrGoToSearch() {
    if (router.currentRoute.value.path === '/kesfet') {
      document.getElementById('discover-search-input')?.focus()
    } else {
      requestSearchFocus()
      void router.push('/kesfet')
    }
  }

  useEventListener(window, 'keydown', (event: KeyboardEvent) => {
    if (event.metaKey || event.ctrlKey || event.altKey) return
    if (isEditableTarget(event.target)) return
    if (document.querySelector('[role="dialog"]')) return

    if (awaitingSecondKey) {
      awaitingSecondKey = false
      if (event.key === 'f') {
        event.preventDefault()
        void router.push('/')
      } else if (event.key === 'k') {
        event.preventDefault()
        void router.push('/kesfet')
      }
      return
    }

    if (event.key === 'g') {
      armGPrefix()
    } else if (event.key === '/') {
      event.preventDefault()
      focusOrGoToSearch()
    } else if (event.key === '?') {
      event.preventDefault()
      helpOpen.value = true
    }
  })

  return { helpOpen }
}
