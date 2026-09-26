import { useMutation } from '@tanstack/vue-query'
import { api } from './client'
import type {
  ChangePasswordIn,
  LoginIn,
  RegisterIn,
  ResetConfirmIn,
  ResetRequestIn,
  ResetVerifyIn,
  TokenOut,
} from '@/types'

export function registerRequest(payload: RegisterIn) {
  return api<TokenOut>('/auth/register', { method: 'POST', body: payload })
}

export function loginRequest(payload: LoginIn) {
  return api<TokenOut>('/auth/login', { method: 'POST', body: payload })
}

export function requestPasswordResetRequest(payload: ResetRequestIn) {
  return api<{ detail: string }>('/auth/password-reset/request', { method: 'POST', body: payload })
}

export function verifyPasswordResetRequest(payload: ResetVerifyIn) {
  return api<{ valid: boolean }>('/auth/password-reset/verify', { method: 'POST', body: payload })
}

export function confirmPasswordResetRequest(payload: ResetConfirmIn) {
  return api<{ detail: string }>('/auth/password-reset/confirm', { method: 'POST', body: payload })
}

export function changePasswordRequest(payload: ChangePasswordIn) {
  return api<TokenOut>('/auth/change-password', { method: 'POST', body: payload })
}

export function logoutAllDevicesRequest() {
  return api<void>('/auth/logout-all', { method: 'POST' })
}

export function useRegister() {
  return useMutation({ mutationFn: registerRequest })
}

export function useLogin() {
  return useMutation({ mutationFn: loginRequest })
}

export function useRequestPasswordReset() {
  return useMutation({ mutationFn: requestPasswordResetRequest })
}

export function useVerifyPasswordReset() {
  return useMutation({ mutationFn: verifyPasswordResetRequest })
}

export function useConfirmPasswordReset() {
  return useMutation({ mutationFn: confirmPasswordResetRequest })
}

export function useChangePassword() {
  return useMutation({ mutationFn: changePasswordRequest })
}

export function useLogoutAllDevices() {
  return useMutation({ mutationFn: logoutAllDevicesRequest })
}
