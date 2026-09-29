<script setup lang="ts">
import { onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { ApiError } from '@/api/client'
import {
  useConfirmPasswordReset,
  useRequestPasswordReset,
  useVerifyPasswordReset,
} from '@/api/auth'
import { validatePasswordsMatch, validatePasswordStrength } from '@/utils/validation'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import OtpInput from '@/components/ui/OtpInput.vue'

const router = useRouter()

const step = ref<1 | 2 | 3>(1)
const email = ref('')
const code = ref('')
const newPassword = ref('')
const newPasswordConfirm = ref('')
const formError = ref('')
const resendIn = ref(0)

let resendTimer: ReturnType<typeof setInterval> | undefined

function startResendCountdown() {
  resendIn.value = 60
  clearInterval(resendTimer)
  resendTimer = setInterval(() => {
    resendIn.value -= 1
    if (resendIn.value <= 0) clearInterval(resendTimer)
  }, 1000)
}

onUnmounted(() => clearInterval(resendTimer))

const requestReset = useRequestPasswordReset()
const verifyReset = useVerifyPasswordReset()
const confirmReset = useConfirmPasswordReset()

async function onRequestSubmit() {
  formError.value = ''
  if (!email.value.trim()) {
    formError.value = 'E-posta gerekli'
    return
  }
  try {
    await requestReset.mutateAsync({ email: email.value.trim() })
    toast.info('Eğer bu e-posta kayıtlıysa sıfırlama kodu gönderildi.')
    startResendCountdown()
    step.value = 2
  } catch {
    formError.value = 'Bir şeyler ters gitti, tekrar dene'
  }
}

async function onResend() {
  if (resendIn.value > 0) return
  try {
    await requestReset.mutateAsync({ email: email.value.trim() })
    toast.info('Kod tekrar gönderildi.')
    startResendCountdown()
  } catch {
    toast.error('Kod gönderilemedi, tekrar dene')
  }
}

async function onVerifySubmit() {
  formError.value = ''
  if (code.value.length !== 6) {
    formError.value = '6 haneli kodu tam gir'
    return
  }
  try {
    await verifyReset.mutateAsync({ email: email.value.trim(), code: code.value })
    step.value = 3
  } catch (error) {
    formError.value = error instanceof ApiError ? error.message : 'Kod doğrulanamadı'
  }
}

async function onConfirmSubmit() {
  formError.value = ''
  const strengthError = validatePasswordStrength(newPassword.value)
  const matchError = validatePasswordsMatch(newPassword.value, newPasswordConfirm.value)
  if (strengthError ?? matchError) {
    formError.value = strengthError ?? matchError ?? ''
    return
  }
  try {
    await confirmReset.mutateAsync({
      email: email.value.trim(),
      code: code.value,
      new_password: newPassword.value,
      new_password_confirm: newPasswordConfirm.value,
    })
    toast.success('Şifren güncellendi, şimdi giriş yapabilirsin.')
    await router.push('/giris')
  } catch (error) {
    formError.value = error instanceof ApiError ? error.message : 'Şifre sıfırlanamadı'
  }
}
</script>

<template>
  <div class="mx-auto flex max-w-sm flex-col gap-6 px-4 py-16">
    <div class="text-center">
      <h1 class="text-2xl font-bold text-fg">Şifremi unuttum</h1>
      <p class="mt-1 text-sm text-muted">Adım {{ step }}/3</p>
    </div>

    <p v-if="formError" role="alert" class="rounded-lg bg-danger/10 px-3 py-2 text-sm text-danger">
      {{ formError }}
    </p>

    <form v-if="step === 1" class="flex flex-col gap-4" novalidate @submit.prevent="onRequestSubmit">
      <p class="text-sm text-muted">Hesabına kayıtlı e-postayı gir, sana bir sıfırlama kodu gönderelim.</p>
      <BaseInput v-model="email" label="E-posta" type="email" autocomplete="email" :disabled="requestReset.isPending.value" />
      <BaseButton type="submit" :loading="requestReset.isPending.value" class="w-full">Kod gönder</BaseButton>
    </form>

    <form v-else-if="step === 2" class="flex flex-col gap-4" novalidate @submit.prevent="onVerifySubmit">
      <p class="text-sm text-muted">{{ email }} adresine gönderilen 6 haneli kodu gir.</p>
      <OtpInput v-model="code" :disabled="verifyReset.isPending.value" />
      <BaseButton type="submit" :loading="verifyReset.isPending.value" class="w-full">Doğrula</BaseButton>
      <button
        type="button"
        class="text-sm text-link hover:underline disabled:cursor-not-allowed disabled:text-muted disabled:no-underline"
        :disabled="resendIn > 0"
        @click="onResend"
      >
        {{ resendIn > 0 ? `Kodu tekrar gönder (${resendIn} sn)` : 'Kodu tekrar gönder' }}
      </button>
    </form>

    <form v-else class="flex flex-col gap-4" novalidate @submit.prevent="onConfirmSubmit">
      <BaseInput
        v-model="newPassword"
        label="Yeni şifre"
        type="password"
        autocomplete="new-password"
        hint="En az 8 karakter, en az bir harf ve bir rakam"
        :disabled="confirmReset.isPending.value"
      />
      <BaseInput
        v-model="newPasswordConfirm"
        label="Yeni şifre (tekrar)"
        type="password"
        autocomplete="new-password"
        :disabled="confirmReset.isPending.value"
      />
      <BaseButton type="submit" :loading="confirmReset.isPending.value" class="w-full">Şifreyi sıfırla</BaseButton>
    </form>

    <RouterLink to="/giris" class="text-center text-sm text-link hover:underline">Girişe dön</RouterLink>
  </div>
</template>
