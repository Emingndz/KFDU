const USERNAME_PATTERN = /^[a-z][a-z0-9_.]{2,29}$/

const RESERVED_USERNAMES = new Set([
  'admin',
  'api',
  'kfdu',
  'ayarlar',
  'kesfet',
  'giris',
  'kayit',
  'u',
  'liste',
  'film',
  'dizi',
  'kitap',
  'asistan',
  'oneriler',
  'bildirimler',
])

export const USERNAME_HINT =
  'Küçük harfle başlamalı; yalnızca küçük harf, rakam, "_" ve "." içerebilir (3-30 karakter)'

export function validateUsername(value: string): string | null {
  const normalized = value.toLowerCase()
  if (!USERNAME_PATTERN.test(normalized)) return USERNAME_HINT
  if (RESERVED_USERNAMES.has(normalized)) return 'Bu kullanıcı adı kullanılamaz'
  return null
}

export function validateEmail(value: string): string | null {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) ? null : 'Geçerli bir e-posta adresi gir'
}

export function validatePasswordStrength(value: string): string | null {
  if (value.length < 8) return 'Şifre en az 8 karakter olmalı'
  if (!/[A-Za-z]/.test(value) || !/\d/.test(value)) return 'Şifre en az bir harf ve bir rakam içermeli'
  return null
}

export function validatePasswordsMatch(password: string, confirm: string): string | null {
  return password === confirm ? null : 'Şifreler eşleşmiyor'
}

export type PasswordStrength = 'zayıf' | 'orta' | 'güçlü'

export function passwordStrength(value: string): PasswordStrength {
  let score = 0
  if (value.length >= 8) score++
  if (value.length >= 12) score++
  if (/[A-Z]/.test(value) && /[a-z]/.test(value)) score++
  if (/\d/.test(value)) score++
  if (/[^A-Za-z0-9]/.test(value)) score++
  if (score <= 2) return 'zayıf'
  if (score <= 3) return 'orta'
  return 'güçlü'
}
