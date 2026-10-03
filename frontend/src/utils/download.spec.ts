import { afterEach, describe, expect, it, vi } from 'vitest'
import { filenameFromDisposition, saveBlob } from './download'

describe('filenameFromDisposition', () => {
  it('tırnaklı ve tırnaksız filename değerini okur', () => {
    expect(filenameFromDisposition('attachment; filename="kfdu-ali-2026-10-04.json"')).toBe('kfdu-ali-2026-10-04.json')
    expect(filenameFromDisposition('attachment; filename=kfdu.csv')).toBe('kfdu.csv')
  })

  it("RFC 5987 filename*= değerini önceler ve çözer", () => {
    const header = `attachment; filename="kutuphane.csv"; filename*=UTF-8''k%C3%BCt%C3%BCphane.csv`
    expect(filenameFromDisposition(header)).toBe('kütüphane.csv')
  })

  it('başlık yoksa ya da ad içermiyorsa null döner', () => {
    expect(filenameFromDisposition(null)).toBeNull()
    expect(filenameFromDisposition('inline')).toBeNull()
  })
})

describe('saveBlob', () => {
  afterEach(() => {
    vi.useRealTimers()
    vi.restoreAllMocks()
  })

  it('geçici bir bağlantıyla indirir, bağlantıyı kaldırır ve nesne URL’sini sonra geri alır', () => {
    vi.useFakeTimers()
    const createObjectURL = vi.fn<(blob: Blob) => string>(() => 'blob:kfdu-test')
    const revokeObjectURL = vi.fn<(url: string) => void>()
    Object.defineProperty(URL, 'createObjectURL', { value: createObjectURL, configurable: true })
    Object.defineProperty(URL, 'revokeObjectURL', { value: revokeObjectURL, configurable: true })
    const clicked: HTMLAnchorElement[] = []
    vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(function (this: HTMLAnchorElement) {
      clicked.push(this)
    })

    saveBlob(new Blob(['type,title\n']), 'kfdu.csv')

    expect(clicked).toHaveLength(1)
    expect(clicked[0]!.download).toBe('kfdu.csv')
    expect(clicked[0]!.href).toBe('blob:kfdu-test')
    expect(document.querySelector('a[download]')).toBeNull()
    expect(revokeObjectURL).not.toHaveBeenCalled()
    vi.advanceTimersByTime(1000)
    expect(revokeObjectURL).toHaveBeenCalledWith('blob:kfdu-test')
  })
})
