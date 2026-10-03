import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import type { LoginIn, MeOut, RegisterIn } from '@/types'
import { loginRequest, registerRequest } from '@/api/auth'
import { ApiError } from '@/api/client'
import { fetchMeRequest } from '@/api/users'

const TOKEN_STORAGE_KEY = 'kfdu_token'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem(TOKEN_STORAGE_KEY))
  const me = ref<MeOut | null>(null)

  const isAuthenticated = computed(() => Boolean(token.value))

  function setToken(value: string | null) {
    token.value = value
    if (value) localStorage.setItem(TOKEN_STORAGE_KEY, value)
    else localStorage.removeItem(TOKEN_STORAGE_KEY)
  }

  function setMe(value: MeOut | null) {
    me.value = value
  }

  async function login(payload: LoginIn) {
    const result = await loginRequest(payload)
    setToken(result.access_token)
    setMe(result.user)
    return result
  }

  async function register(payload: RegisterIn) {
    const result = await registerRequest(payload)
    setToken(result.access_token)
    setMe(result.user)
    return result
  }

  function logout() {
    setToken(null)
    setMe(null)
  }

  async function fetchMe() {
    try {
      const result = await fetchMeRequest()
      setMe(result)
      return result
    } catch (error) {
      // Yalnız oturum gerçekten geçersizse (401) çıkış yapılır. Ağ yokken (çevrimdışı açılan PWA) ya da
      // sunucu geçici hata verirken token korunur; aksi halde kullanıcı sebepsiz yere oturumdan atılırdı.
      if (error instanceof ApiError && error.status === 401) {
        setToken(null)
        setMe(null)
      }
      throw error
    }
  }

  return { token, me, isAuthenticated, login, register, logout, fetchMe, setMe, setToken }
})
