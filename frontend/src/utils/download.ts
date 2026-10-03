/** `attachment; filename="kfdu.json"` ya da RFC 5987 `filename*=UTF-8''...` başlığından dosya adını çıkarır. */
export function filenameFromDisposition(header: string | null): string | null {
  if (!header) return null
  const encoded = /filename\*=UTF-8''([^;]+)/i.exec(header)?.[1]
  if (encoded) {
    try {
      return decodeURIComponent(encoded.trim())
    } catch {
      // bozuk kodlama: düz filename= değerine düş
    }
  }
  return /filename="?([^";]+)"?/i.exec(header)?.[1]?.trim() || null
}

/** Blob'u dosya olarak indirtir (geçici nesne URL'si + görünmez bağlantı). */
export function saveBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  // İndirme tıklamadan hemen sonra başlar; URL aynı anda geri alınırsa bazı tarayıcılar indirmeyi iptal ediyor
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}
