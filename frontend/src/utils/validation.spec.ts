import { describe, expect, it } from 'vitest'
import {
  passwordStrength,
  validateEmail,
  validatePasswordsMatch,
  validatePasswordStrength,
  validateUsername,
} from './validation'

describe('validateUsername', () => {
  it('geçerli kullanıcı adını kabul eder', () => {
    expect(validateUsername('emin.dev')).toBeNull()
    expect(validateUsername('a12')).toBeNull()
  })

  it('büyük harfleri küçültüp doğrular', () => {
    expect(validateUsername('Emin')).toBeNull()
  })

  it('rakamla başlayan adı reddeder', () => {
    expect(validateUsername('1emin')).not.toBeNull()
  })

  it('3 karakterden kısa adı reddeder', () => {
    expect(validateUsername('ab')).not.toBeNull()
  })

  it('izin verilmeyen karakter içeren adı reddeder', () => {
    expect(validateUsername('emin-dev')).not.toBeNull()
    expect(validateUsername('emin dev')).not.toBeNull()
  })

  it('ayrılmış kullanıcı adlarını reddeder', () => {
    expect(validateUsername('admin')).not.toBeNull()
    expect(validateUsername('giris')).not.toBeNull()
  })
})

describe('validateEmail', () => {
  it('geçerli e-postayı kabul eder', () => {
    expect(validateEmail('a@b.com')).toBeNull()
  })

  it('geçersiz e-postayı reddeder', () => {
    expect(validateEmail('gecersiz')).not.toBeNull()
    expect(validateEmail('a@b')).not.toBeNull()
  })
})

describe('validatePasswordStrength', () => {
  it('en az 8 karakter, harf ve rakam şartını kabul eder', () => {
    expect(validatePasswordStrength('sifre123')).toBeNull()
  })

  it('kısa şifreyi reddeder', () => {
    expect(validatePasswordStrength('a1b2c3')).not.toBeNull()
  })

  it('yalnızca harf içeren şifreyi reddeder', () => {
    expect(validatePasswordStrength('sadecelaraf')).not.toBeNull()
  })

  it('yalnızca rakam içeren şifreyi reddeder', () => {
    expect(validatePasswordStrength('12345678')).not.toBeNull()
  })
})

describe('validatePasswordsMatch', () => {
  it('eşleşen şifrelerde null döner', () => {
    expect(validatePasswordsMatch('sifre123', 'sifre123')).toBeNull()
  })

  it('eşleşmeyen şifrelerde hata döner', () => {
    expect(validatePasswordsMatch('sifre123', 'sifre124')).not.toBeNull()
  })
})

describe('passwordStrength', () => {
  it('kısa/basit şifreyi zayıf olarak işaretler', () => {
    expect(passwordStrength('abcdefgh')).toBe('zayıf')
  })

  it('uzun ve çeşitli şifreyi güçlü olarak işaretler', () => {
    expect(passwordStrength('Sifr3m!Guclu2026')).toBe('güçlü')
  })
})
