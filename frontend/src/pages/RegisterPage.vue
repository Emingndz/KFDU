<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ApiError } from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import {
  passwordStrength,
  USERNAME_HINT,
  validateEmail,
  validatePasswordsMatch,
  validatePasswordStrength,
  validateUsername,
} from '@/utils/validation'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseInput from '@/components/ui/BaseInput.vue'

const auth = useAuthStore()
const router = useRouter()

const username = ref('')
const email = ref('')
const password = ref('')
const passwordConfirm = ref('')
const formError = ref('')
const submitting = ref(false)
const touched = ref({ username: false, email: false, password: false, passwordConfirm: false })
const serverFieldErrors = ref<{ username?: string; email?: string }>({})

watch(username, () => (serverFieldErrors.value.username = undefined))
watch(email, () => (serverFieldErrors.value.email = undefined))

const usernameError = computed(
  () => serverFieldErrors.value.username ?? (touched.value.username ? validateUsername(username.value) : null),
)
const emailError = computed(
  () => serverFieldErrors.value.email ?? (touched.value.email ? validateEmail(email.value) : null),
)
const passwordError = computed(() => (touched.value.password ? validatePasswordStrength(password.value) : null))
const passwordConfirmError = computed(() =>
  touched.value.passwordConfirm ? validatePasswordsMatch(password.value, passwordConfirm.value) : null,
)
const strength = computed(() => (password.value ? passwordStrength(password.value) : null))
const strengthClass = computed(() => {
  if (strength.value === 'zayıf') return 'text-danger'
  if (strength.value === 'orta') return 'text-warning'
  return 'text-success'
})

function validateAll(): boolean {
  touched.value = { username: true, email: true, password: true, passwordConfirm: true }
  return (
    !validateUsername(username.value) &&
    !validateEmail(email.value) &&
    !validatePasswordStrength(password.value) &&
    !validatePasswordsMatch(password.value, passwordConfirm.value)
  )
}

async function onSubmit() {
  if (submitting.value) return
  formError.value = ''
  serverFieldErrors.value = {}
  if (!validateAll()) return

  submitting.value = true
  try {
    await auth.register({
      username: username.value.toLowerCase(),
      email: email.value,
      password: password.value,
      password_confirm: passwordConfirm.value,
    })
    await router.push('/hosgeldin')
  } catch (error) {
    if (error instanceof ApiError && error.code === 'EMAIL_TAKEN') {
      serverFieldErrors.value.email = error.message
    } else if (error instanceof ApiError && error.code === 'USERNAME_TAKEN') {
      serverFieldErrors.value.username = error.message
    } else {
      formError.value = error instanceof ApiError ? error.message : 'Kayıt olunamadı, tekrar dene'
    }
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="mx-auto flex max-w-sm flex-col gap-6 px-4 py-16">
    <div class="text-center">
      <h1 class="text-2xl font-bold text-fg">Kayıt ol</h1>
      <p class="mt-1 text-sm text-muted">Filmlerini, dizilerini ve kitaplarını takip etmeye başla</p>
    </div>

    <form class="flex flex-col gap-4" novalidate @submit.prevent="onSubmit">
      <p v-if="formError" role="alert" class="rounded-lg bg-danger/10 px-3 py-2 text-sm text-danger">
        {{ formError }}
      </p>

      <BaseInput
        v-model="username"
        label="Kullanıcı adı"
        autocomplete="username"
        :hint="USERNAME_HINT"
        :error="usernameError ?? undefined"
        :disabled="submitting"
        @blur="touched.username = true"
      />

      <BaseInput
        v-model="email"
        label="E-posta"
        type="email"
        autocomplete="email"
        :error="emailError ?? undefined"
        :disabled="submitting"
        @blur="touched.email = true"
      />

      <div class="flex flex-col gap-1.5">
        <BaseInput
          v-model="password"
          label="Şifre"
          type="password"
          autocomplete="new-password"
          hint="En az 8 karakter, en az bir harf ve bir rakam"
          :error="passwordError ?? undefined"
          :disabled="submitting"
          @blur="touched.password = true"
        />
        <p v-if="strength && !passwordError" class="text-xs" :class="strengthClass">Şifre gücü: {{ strength }}</p>
      </div>

      <BaseInput
        v-model="passwordConfirm"
        label="Şifre (tekrar)"
        type="password"
        autocomplete="new-password"
        :error="passwordConfirmError ?? undefined"
        :disabled="submitting"
        @blur="touched.passwordConfirm = true"
      />

      <BaseButton type="submit" :loading="submitting" class="w-full">Kayıt ol</BaseButton>
    </form>

    <p class="text-center text-sm text-muted">
      Zaten hesabın var mı?
      <RouterLink to="/giris" class="font-medium text-brand-600 hover:underline">Giriş yap</RouterLink>
    </p>
  </div>
</template>
