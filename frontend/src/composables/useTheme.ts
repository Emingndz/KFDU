import { useColorMode } from '@vueuse/core'

export type ThemeChoice = 'auto' | 'light' | 'dark'

export const themeOptions: { value: ThemeChoice; label: string }[] = [
  { value: 'auto', label: 'Sistem' },
  { value: 'light', label: 'Açık' },
  { value: 'dark', label: 'Koyu' },
]

export function useTheme() {
  const mode = useColorMode({
    attribute: 'class',
    modes: { light: '', dark: 'dark' },
    storageKey: 'kfdu-theme',
  })

  return { mode, options: themeOptions }
}
