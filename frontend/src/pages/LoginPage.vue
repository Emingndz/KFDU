<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ApiError } from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseInput from '@/components/ui/BaseInput.vue'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const login = ref('')
const password = ref('')
const formError = ref('')
const submitting = ref(false)
const capsLockOn = ref(false)

function checkCapsLock(event: KeyboardEvent) {
  capsLockOn.value = event.getModifierState?.('CapsLock') ?? false
}

async function onSubmit() {
  if (submitting.value) return
  formError.value = ''
  if (!login.value.trim() || !password.value) {
    formError.value = 'E-posta/kullanıcı adı ve şifre gerekli'
    return
  }

  submitting.value = true
  try {
    await auth.login({ login: login.value.trim(), password: password.value })
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/'
    await router.push(redirect)
  } catch (error) {
    formError.value = error instanceof ApiError ? error.message : 'Giriş yapılamadı, tekrar dene'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="mx-auto flex max-w-sm flex-col gap-6 px-4 py-16">
    <div class="text-center">
      <h1 class="text-2xl font-bold text-fg">Giriş yap</h1>
      <p class="mt-1 text-sm text-muted">KFDU'ya hoş geldin</p>
    </div>

    <form class="flex flex-col gap-4" novalidate @submit.prevent="onSubmit">
      <p v-if="formError" role="alert" class="rounded-lg bg-danger/10 px-3 py-2 text-sm text-danger">
        {{ formError }}
      </p>

      <BaseInput v-model="login" label="E-posta veya kullanıcı adı" autocomplete="username" :disabled="submitting" />

      <div class="flex flex-col gap-1.5">
        <BaseInput
          v-model="password"
          label="Şifre"
          type="password"
          autocomplete="current-password"
          :disabled="submitting"
          @keydown="checkCapsLock"
          @keyup="checkCapsLock"
        />
        <p v-if="capsLockOn" class="text-xs text-warning">Caps Lock açık</p>
      </div>

      <BaseButton type="submit" :loading="submitting" class="w-full">Giriş yap</BaseButton>
    </form>

    <div class="flex flex-col items-center gap-2 text-sm">
      <RouterLink to="/sifremi-unuttum" class="text-link hover:underline">Şifremi unuttum</RouterLink>
      <p class="text-muted">
        Hesabın yok mu?
        <RouterLink to="/kayit" class="font-medium text-link hover:underline">Kayıt ol</RouterLink>
      </p>
    </div>
  </div>
</template>
