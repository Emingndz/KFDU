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

export type GenreOut = components['schemas']['GenreOut']

export type ContentSummary = components['schemas']['ContentSummary']
export type ContentDetail = components['schemas']['ContentDetail']
export type Person = components['schemas']['Person']
export type Providers = components['schemas']['Providers']

export type LibraryStatus = components['schemas']['LibraryStatus']
export type EntryOut = components['schemas']['EntryOut']
export type EntryUpdateIn = components['schemas']['EntryUpdateIn']
export type ContentState = components['schemas']['ContentState']
export type PlatformStats = components['schemas']['PlatformStats']
export type MeState = components['schemas']['MeState']
export type FriendEntry = components['schemas']['FriendEntry']
export type LookupEntryOut = components['schemas']['LookupEntryOut']
export type ReviewCreateIn = components['schemas']['ReviewCreateIn']
export type ReviewUpdateIn = components['schemas']['ReviewUpdateIn']
export type ReviewBasicOut = components['schemas']['ReviewBasicOut']
export type ReviewOut = components['schemas']['ReviewOut']
export type ReviewDetail = components['schemas']['ReviewDetail']

export type ListCreateIn = components['schemas']['ListCreateIn']
export type ListUpdateIn = components['schemas']['ListUpdateIn']
export type ListItemIn = components['schemas']['ListItemIn']
export type ListOut = components['schemas']['ListOut']
export type ListDetail = components['schemas']['ListDetail']
export type ListItemOut = components['schemas']['ListItemOut']
export type MyListOut = components['schemas']['MyListOut']
