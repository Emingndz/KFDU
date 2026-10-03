<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { ApiError } from '@/api/client'
import { useChangeEmail, useDeleteAccount, useUpdateMe } from '@/api/users'
import { useChangePassword, useLogoutAllDevices } from '@/api/auth'
import { useGenres } from '@/api/catalog'
import { useDownloadExport } from '@/api/transfer'
import { useAuthStore } from '@/stores/auth'
import { useConfirm } from '@/composables/useConfirm'
import { useTheme } from '@/composables/useTheme'
import { passwordStrength, validateEmail, validatePasswordStrength, validatePasswordsMatch } from '@/utils/validation'
import { FileJson, FileSpreadsheet } from 'lucide-vue-next'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import ProfileForm from '@/components/users/ProfileForm.vue'
import GenreChipPicker from '@/components/users/GenreChipPicker.vue'
import ImportCard from '@/components/transfer/ImportCard.vue'
import type { ExportFormat } from '@/types'

const router = useRouter()
const auth = useAuthStore()
const { confirm } = useConfirm()
const { mode, options: themeOptions } = useTheme()

// --- Hesap: e-posta değiştir ---
const newEmail = ref('')
const emailPassword = ref('')
const emailTouched = ref(false)
const emailPasswordError = ref('')
const newEmailError = computed(() => (emailTouched.value ? validateEmail(newEmail.value) : null))

const changeEmail = useChangeEmail()

async function submitEmailChange() {
  emailTouched.value = true
  emailPasswordError.value = ''
  if (validateEmail(newEmail.value) || !emailPassword.value) return
  try {
    const updated = await changeEmail.mutateAsync({ new_email: newEmail.value, current_password: emailPassword.value })
    auth.setMe(updated)
    toast.success('E-posta adresin güncellendi')
    newEmail.value = ''
    emailPassword.value = ''
    emailTouched.value = false
  } catch (error) {
    if (error instanceof ApiError && error.code === 'INVALID_PASSWORD') emailPasswordError.value = error.message
    else toast.error(error instanceof ApiError ? error.message : 'E-posta güncellenemedi')
  }
}

// --- Güvenlik: şifre değiştir ---
const currentPassword = ref('')
const newPassword = ref('')
const newPasswordConfirm = ref('')
const pwTouched = ref(false)
const currentPasswordError = ref('')
const newPasswordError = computed(() => (pwTouched.value ? validatePasswordStrength(newPassword.value) : null))
const newPasswordConfirmError = computed(() =>
  pwTouched.value ? validatePasswordsMatch(newPassword.value, newPasswordConfirm.value) : null,
)
const strength = computed(() => (newPassword.value ? passwordStrength(newPassword.value) : null))
const strengthClass = computed(() => {
  if (strength.value === 'zayıf') return 'text-danger'
  if (strength.value === 'orta') return 'text-warning'
  return 'text-success'
})

const changePassword = useChangePassword()

async function submitPasswordChange() {
  pwTouched.value = true
  currentPasswordError.value = ''
  if (!currentPassword.value || validatePasswordStrength(newPassword.value) || validatePasswordsMatch(newPassword.value, newPasswordConfirm.value)) return
  try {
    const result = await changePassword.mutateAsync({
      current_password: currentPassword.value,
      new_password: newPassword.value,
      new_password_confirm: newPasswordConfirm.value,
    })
    auth.setToken(result.access_token)
    auth.setMe(result.user)
    toast.success('Şifren güncellendi')
    currentPassword.value = ''
    newPassword.value = ''
    newPasswordConfirm.value = ''
    pwTouched.value = false
  } catch (error) {
    if (error instanceof ApiError && error.code === 'INVALID_PASSWORD') currentPasswordError.value = error.message
    else toast.error(error instanceof ApiError ? error.message : 'Şifre güncellenemedi')
  }
}

const logoutAllDevices = useLogoutAllDevices()
async function submitLogoutAll() {
  const ok = await confirm({
    title: 'Tüm cihazlardan çıkış yap',
    message: 'Bu işlem şu an içinde bulunduğun oturum dahil tüm cihazlardaki oturumları kapatır.',
    confirmText: 'Evet, hepsinden çık',
    danger: true,
  })
  if (!ok) return
  try {
    await logoutAllDevices.mutateAsync()
    auth.logout()
    toast.success('Tüm cihazlardan çıkış yapıldı')
    void router.push('/kesfet')
  } catch {
    toast.error('Bir şeyler ters gitti, tekrar dene')
  }
}

// --- Tercihler: favori türler ---
const movieGenres = useGenres('movie')
const tvGenres = useGenres('tv')
const bookGenres = useGenres('book')

const movieTvGenres = computed(() => {
  const byKey = new Map<string, { key: string; label: string }>()
  for (const g of movieGenres.data.value ?? []) byKey.set(g.key, g)
  for (const g of tvGenres.data.value ?? []) byKey.set(g.key, g)
  return [...byKey.values()]
})

const selectedGenres = ref(new Set(auth.me?.favorite_genres ?? []))
function toggleGenre(key: string) {
  if (selectedGenres.value.has(key)) selectedGenres.value.delete(key)
  else selectedGenres.value.add(key)
}

const updateGenres = useUpdateMe()
async function saveGenres() {
  try {
    const updated = await updateGenres.mutateAsync({ favorite_genres: [...selectedGenres.value] })
    auth.setMe(updated)
    toast.success('Tercihlerin kaydedildi')
  } catch {
    toast.error('Tercihler kaydedilemedi')
  }
}

// --- Verilerim: dışa aktar ---
const downloadExport = useDownloadExport()
const exportingFormat = computed(() => (downloadExport.isPending.value ? downloadExport.variables.value : null))

async function exportData(format: ExportFormat) {
  try {
    await downloadExport.mutateAsync(format)
    toast.success('Dosyan indirildi')
  } catch (error) {
    toast.error(error instanceof ApiError ? error.message : 'Dosya hazırlanamadı, tekrar dene')
  }
}

// --- Tehlikeli bölge: hesabı sil ---
const deletePassword = ref('')
const deleteConfirmText = ref('')
const deletePasswordError = ref('')
const canDelete = computed(() => deletePassword.value.length > 0 && deleteConfirmText.value === 'SİL')

const deleteAccount = useDeleteAccount()
async function submitDeleteAccount() {
  if (!canDelete.value) return
  deletePasswordError.value = ''
  try {
    await deleteAccount.mutateAsync({ password: deletePassword.value })
    auth.logout()
    toast.success('Hesabın silindi')
    void router.push('/kesfet')
  } catch (error) {
    if (error instanceof ApiError && error.code === 'INVALID_PASSWORD') deletePasswordError.value = error.message
    else toast.error(error instanceof ApiError ? error.message : 'Hesap silinemedi')
  }
}
</script>

<template>
  <div class="mx-auto flex max-w-2xl flex-col gap-8 py-6">
    <h1 class="text-2xl font-bold text-fg">Ayarlar</h1>

    <section class="flex flex-col gap-4 rounded-card border border-border p-4">
      <h2 class="text-lg font-semibold text-fg">Profil</h2>
      <ProfileForm />
    </section>

    <section class="flex flex-col gap-4 rounded-card border border-border p-4">
      <h2 class="text-lg font-semibold text-fg">Hesap</h2>
      <p class="text-sm text-muted">Şu anki e-posta: <span class="text-fg">{{ auth.me?.email }}</span></p>
      <BaseInput v-model="newEmail" type="email" label="Yeni e-posta" :error="newEmailError ?? undefined" autocomplete="email" />
      <BaseInput v-model="emailPassword" type="password" label="Mevcut şifre" :error="emailPasswordError || undefined" autocomplete="current-password" />
      <div class="flex justify-end">
        <BaseButton :loading="changeEmail.isPending.value" @click="submitEmailChange">E-postayı güncelle</BaseButton>
      </div>
    </section>

    <section class="flex flex-col gap-4 rounded-card border border-border p-4">
      <h2 class="text-lg font-semibold text-fg">Güvenlik</h2>

      <div class="flex flex-col gap-3">
        <BaseInput v-model="currentPassword" type="password" label="Mevcut şifre" :error="currentPasswordError || undefined" autocomplete="current-password" />
        <div>
          <BaseInput v-model="newPassword" type="password" label="Yeni şifre" :error="newPasswordError ?? undefined" autocomplete="new-password" />
          <p v-if="strength && !newPasswordError" class="mt-1 text-xs" :class="strengthClass">Şifre gücü: {{ strength }}</p>
        </div>
        <BaseInput v-model="newPasswordConfirm" type="password" label="Yeni şifre (tekrar)" :error="newPasswordConfirmError ?? undefined" autocomplete="new-password" />
        <div class="flex justify-end">
          <BaseButton :loading="changePassword.isPending.value" @click="submitPasswordChange">Şifreyi değiştir</BaseButton>
        </div>
      </div>

      <div class="flex items-center justify-between gap-4 border-t border-border pt-4">
        <div>
          <p class="text-sm font-medium text-fg">Tüm cihazlardan çıkış yap</p>
          <p class="text-xs text-muted">Bu cihaz dahil, hesabına giriş yapılmış tüm oturumları kapatır.</p>
        </div>
        <BaseButton variant="secondary" :loading="logoutAllDevices.isPending.value" @click="submitLogoutAll">Çıkış yap</BaseButton>
      </div>
    </section>

    <section class="flex flex-col gap-4 rounded-card border border-border p-4">
      <h2 class="text-lg font-semibold text-fg">Görünüm</h2>
      <div class="flex gap-2">
        <button
          v-for="option in themeOptions"
          :key="option.value"
          type="button"
          class="rounded-full border px-3 py-1.5 text-sm transition motion-safe:duration-150"
          :class="mode === option.value ? 'border-brand-500 bg-brand-500/15 text-link' : 'border-border bg-surface text-fg hover:bg-surface-2'"
          :aria-pressed="mode === option.value"
          @click="mode = option.value"
        >
          {{ option.label }}
        </button>
      </div>
    </section>

    <section class="flex flex-col gap-4 rounded-card border border-border p-4">
      <h2 class="text-lg font-semibold text-fg">Tercihler</h2>
      <div class="flex flex-col gap-2">
        <p class="text-sm text-muted">Film / dizi türleri</p>
        <GenreChipPicker :genres="movieTvGenres" :selected="selectedGenres" @toggle="toggleGenre" />
      </div>
      <div class="flex flex-col gap-2">
        <p class="text-sm text-muted">Kitap türleri</p>
        <GenreChipPicker :genres="bookGenres.data.value ?? []" :selected="selectedGenres" @toggle="toggleGenre" />
      </div>
      <div class="flex justify-end">
        <BaseButton :loading="updateGenres.isPending.value" @click="saveGenres">Tercihleri kaydet</BaseButton>
      </div>
    </section>

    <section class="flex flex-col gap-4 rounded-card border border-border p-4">
      <div>
        <h2 class="text-lg font-semibold text-fg">Verilerim</h2>
        <p class="text-sm text-muted">Verilerin senin: istediğin zaman indir ya da başka platformlardan getir.</p>
      </div>

      <div class="flex flex-col gap-3">
        <div>
          <h3 class="text-sm font-semibold text-fg">Dışa aktar</h3>
          <p class="text-sm text-muted">Kütüphanen, puanların, incelemelerin ve listelerin tek dosyada.</p>
        </div>
        <div class="flex flex-wrap gap-2">
          <BaseButton
            variant="secondary"
            :loading="exportingFormat === 'json'"
            :disabled="exportingFormat !== null"
            @click="exportData('json')"
          >
            <template #icon><FileJson class="size-4" aria-hidden="true" /></template>
            JSON indir
          </BaseButton>
          <BaseButton
            variant="secondary"
            :loading="exportingFormat === 'csv'"
            :disabled="exportingFormat !== null"
            @click="exportData('csv')"
          >
            <template #icon><FileSpreadsheet class="size-4" aria-hidden="true" /></template>
            CSV indir (Excel)
          </BaseButton>
        </div>
      </div>

      <div class="flex flex-col gap-3 border-t border-border pt-4">
        <div>
          <h3 class="text-sm font-semibold text-fg">İçe aktar</h3>
          <p class="text-sm text-muted">
            Mevcut puanların ve durumların korunur, yalnız eksikler tamamlanır. İçe aktarılanlar takipçilerinin akışına
            düşmez.
          </p>
        </div>
        <div class="grid gap-3 md:grid-cols-2">
          <ImportCard source="letterboxd" />
          <ImportCard source="goodreads" />
        </div>
      </div>
    </section>

    <section class="flex flex-col gap-4 rounded-card border border-danger/40 p-4">
      <h2 class="text-lg font-semibold text-danger">Tehlikeli bölge</h2>
      <p class="text-sm text-muted">Hesabını sildiğinde tüm verilerin kalıcı olarak kaldırılır. Bu işlem geri alınamaz.</p>
      <BaseInput v-model="deletePassword" type="password" label="Şifren" :error="deletePasswordError || undefined" autocomplete="current-password" />
      <BaseInput v-model="deleteConfirmText" label="Onaylamak için “SİL” yaz" placeholder="SİL" />
      <div class="flex justify-end">
        <BaseButton variant="danger" :disabled="!canDelete" :loading="deleteAccount.isPending.value" @click="submitDeleteAccount">
          Hesabımı kalıcı olarak sil
        </BaseButton>
      </div>
    </section>
  </div>
</template>
