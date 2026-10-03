import { defineConfig, minimal2023Preset } from '@vite-pwa/assets-generator/config'

// İkonlar public/favicon.svg'den üretilir: npx pwa-assets-generator
// Maskable (Android) ve Apple ikonları işletim sisteminin kendi maskesiyle kırpılır; varsayılan beyaz dolgu
// yerine marka rengiyle tam dolu üretilir (glif güvenli bölgenin içinde kalıyor).
const brandFill = { padding: 0, resizeOptions: { background: '#6a47ff' } }

export default defineConfig({
  headLinkOptions: { preset: '2023' },
  preset: {
    ...minimal2023Preset,
    maskable: { ...minimal2023Preset.maskable, ...brandFill },
    apple: { ...minimal2023Preset.apple, ...brandFill },
  },
  images: ['public/favicon.svg'],
})
