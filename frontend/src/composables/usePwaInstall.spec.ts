import { beforeEach, describe, expect, it, vi } from 'vitest'

function fakeInstallEvent(outcome: 'accepted' | 'dismissed') {
  const prompt = vi.fn<() => Promise<void>>().mockResolvedValue(undefined)
  const event = Object.assign(new Event('beforeinstallprompt', { cancelable: true }), {
    prompt,
    userChoice: Promise.resolve({ outcome, platform: 'web' }),
  })
  return { event, prompt }
}

// Modül düzeyindeki durum (yakalanan olay) her testte sıfırdan başlasın
async function loadComposable() {
  vi.resetModules()
  const { usePwaInstall } = await import('./usePwaInstall')
  return usePwaInstall()
}

describe('usePwaInstall', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('beforeinstallprompt yakalanınca kurulabilir olur ve tarayıcının kendi çubuğu bastırılır', async () => {
    const { canInstall } = await loadComposable()
    expect(canInstall.value).toBe(false)

    const { event } = fakeInstallEvent('accepted')
    window.dispatchEvent(event)

    expect(event.defaultPrevented).toBe(true)
    expect(canInstall.value).toBe(true)
  })

  it('kurulum penceresini bir kez açar; kabulde true döner ve düğme gizlenir', async () => {
    const { canInstall, install } = await loadComposable()
    const { event, prompt } = fakeInstallEvent('accepted')
    window.dispatchEvent(event)

    await expect(install()).resolves.toBe(true)
    expect(prompt).toHaveBeenCalledTimes(1)
    expect(canInstall.value).toBe(false)
    await expect(install()).resolves.toBe(false)
    expect(prompt).toHaveBeenCalledTimes(1)
  })

  it('kullanıcı vazgeçerse false döner', async () => {
    const { install } = await loadComposable()
    window.dispatchEvent(fakeInstallEvent('dismissed').event)
    await expect(install()).resolves.toBe(false)
  })

  it('uygulama başka yoldan yüklenirse (appinstalled) düğme gizlenir', async () => {
    const { canInstall } = await loadComposable()
    window.dispatchEvent(fakeInstallEvent('accepted').event)
    expect(canInstall.value).toBe(true)

    window.dispatchEvent(new Event('appinstalled'))
    expect(canInstall.value).toBe(false)
  })
})
