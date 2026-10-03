import { computed, shallowRef } from 'vue'

// Standart DOM tiplerinde yok (yalnız Chromium tabanlı tarayıcılar destekliyor)
interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed'; platform: string }>
}

const deferredPrompt = shallowRef<BeforeInstallPromptEvent | null>(null)
let listening = false

/**
 * Olay sayfa yüklenir yüklenmez gelebilir; bileşen bağlanmadan kaçmasın diye main.ts'te erkenden çağrılır.
 * Tarayıcının kendi kurulum bilgi çubuğu bastırılır, kurulum kullanıcı menüsündeki düğmeden yapılır.
 */
export function listenForInstallPrompt(): void {
  if (listening) return
  listening = true
  window.addEventListener('beforeinstallprompt', (event) => {
    event.preventDefault()
    deferredPrompt.value = event as BeforeInstallPromptEvent
  })
  window.addEventListener('appinstalled', () => {
    deferredPrompt.value = null
  })
}

export function usePwaInstall() {
  listenForInstallPrompt()
  const canInstall = computed(() => deferredPrompt.value !== null)

  /** Kurulum penceresini açar; kullanıcı kabul ederse true döner. */
  async function install(): Promise<boolean> {
    const event = deferredPrompt.value
    if (!event) return false
    deferredPrompt.value = null // prompt() olay başına yalnız bir kez çağrılabilir
    await event.prompt()
    const { outcome } = await event.userChoice
    return outcome === 'accepted'
  }

  return { canInstall, install }
}
