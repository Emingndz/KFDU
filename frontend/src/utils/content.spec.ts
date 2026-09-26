import { describe, expect, it } from 'vitest'
import { contentKey, contentPath, statusLabel, statusOptions, typeLabel } from './content'

describe('typeLabel', () => {
  it('her tür için doğru Türkçe etiketi döner', () => {
    expect(typeLabel('movie')).toBe('Film')
    expect(typeLabel('tv')).toBe('Dizi')
    expect(typeLabel('book')).toBe('Kitap')
  })
})

describe('contentPath', () => {
  it('türe göre doğru yolu üretir', () => {
    expect(contentPath('movie', 27205)).toBe('/film/27205')
    expect(contentPath('tv', 1396)).toBe('/dizi/1396')
    expect(contentPath('book', 'OL45804W')).toBe('/kitap/OL45804W')
  })
})

describe('contentKey', () => {
  it('tür:id biçiminde anahtar üretir', () => {
    expect(contentKey('movie', 27205)).toBe('movie:27205')
  })
})

describe('statusLabel', () => {
  it('film/dizi için izleme etiketlerini döner', () => {
    expect(statusLabel('completed', 'movie')).toBe('İzledim')
    expect(statusLabel('in_progress', 'tv')).toBe('İzliyorum')
  })

  it('kitap için okuma etiketlerini döner', () => {
    expect(statusLabel('completed', 'book')).toBe('Okudum')
    expect(statusLabel('planned', 'book')).toBe('Okuyacağım')
  })

  it('yarım bırakma etiketi türden bağımsız aynıdır', () => {
    expect(statusLabel('dropped', 'movie')).toBe('Yarım bıraktım')
    expect(statusLabel('dropped', 'book')).toBe('Yarım bıraktım')
  })
})

describe('statusOptions', () => {
  it('4 seçeneği doğru sırayla döner', () => {
    const options = statusOptions('book')
    expect(options.map((o) => o.value)).toEqual(['completed', 'in_progress', 'planned', 'dropped'])
    expect(options[0]).toEqual({ value: 'completed', label: 'Okudum' })
  })
})
