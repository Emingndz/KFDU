import type { components } from '@/api/schema'

export type PublicUserOut = components['schemas']['PublicUserOut']
export type PublicUserWithFollowOut = components['schemas']['PublicUserWithFollowOut']
export type MeOut = components['schemas']['MeOut']
export type ProfileOut = components['schemas']['ProfileOut']
export type MeUpdateIn = components['schemas']['MeUpdateIn']
export type EmailChangeIn = components['schemas']['EmailChangeIn']
export type DeleteAccountIn = components['schemas']['DeleteAccountIn']

export type RegisterIn = components['schemas']['RegisterIn']
export type LoginIn = components['schemas']['LoginIn']
export type TokenOut = components['schemas']['TokenOut']
export type ResetRequestIn = components['schemas']['ResetRequestIn']
export type ResetVerifyIn = components['schemas']['ResetVerifyIn']
export type ResetConfirmIn = components['schemas']['ResetConfirmIn']
export type ChangePasswordIn = components['schemas']['ChangePasswordIn']

export type Page<T> = { items: T[]; page: number; page_size: number; total: number | null; has_next: boolean }
export type CursorPage<T> = { items: T[]; next_cursor: string | null }
