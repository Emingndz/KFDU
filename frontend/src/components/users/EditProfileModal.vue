<script setup lang="ts">
import { ref, watch } from 'vue'
import { toast } from 'vue-sonner'
import { ApiError } from '@/api/client'
import { useRemoveAvatar, useUpdateMe, useUploadAvatar } from '@/api/users'
import { useAuthStore } from '@/stores/auth'
import { USERNAME_HINT, validateUsername } from '@/utils/validation'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseTextarea from '@/components/ui/BaseTextarea.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseAvatar from '@/components/ui/BaseAvatar.vue'

const open = defineModel<boolean>({ default: false })
const auth = useAuthStore()

const displayName = ref('')
const bio = ref('')
const username = ref('')
const usernameError = ref('')
const avatarPreview = ref<string | null>(null)
const avatarFile = ref<File | null>(null)

watch(open, (isOpen) => {
  if (isOpen && auth.me) {
    displayName.value = auth.me.display_name ?? ''
    bio.value = auth.me.bio ?? ''
    username.value = auth.me.username
    usernameError.value = ''
    avatarPreview.value = null
    avatarFile.value = null
  }
})

const updateMe = useUpdateMe()
const uploadAvatar = useUploadAvatar()
const removeAvatar = useRemoveAvatar()

function onFileChange(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return
  avatarFile.value = file
  avatarPreview.value = URL.createObjectURL(file)
}

async function save() {
  usernameError.value = ''
  const usernameProblem = validateUsername(username.value)
  if (usernameProblem) {
    usernameError.value = usernameProblem
    return
  }
  try {
    if (avatarFile.value) await uploadAvatar.mutateAsync(avatarFile.value)
    await updateMe.mutateAsync({
      display_name: displayName.value || null,
      bio: bio.value || null,
      username: username.value.toLowerCase(),
    })
    toast.success('Profil güncellendi')
    open.value = false
  } catch (error) {
    if (error instanceof ApiError && error.code === 'USERNAME_TAKEN') usernameError.value = error.message
    else toast.error(error instanceof ApiError ? error.message : 'Profil güncellenemedi')
  }
}

async function onRemoveAvatar() {
  try {
    await removeAvatar.mutateAsync()
    toast.success('Avatar kaldırıldı')
  } catch {
    toast.error('Avatar kaldırılamadı')
  }
}
</script>

<template>
  <BaseModal v-model="open" title="Profili düzenle">
    <div class="flex flex-col gap-4">
      <div class="flex items-center gap-3">
        <BaseAvatar :name="displayName || username" :src="avatarPreview ?? auth.me?.avatar_url" size="xl" />
        <div class="flex flex-col gap-2">
          <label class="cursor-pointer text-sm font-medium text-brand-600 hover:underline">
            Fotoğraf yükle
            <input type="file" accept="image/*" class="hidden" @change="onFileChange" />
          </label>
          <button v-if="auth.me?.avatar_url" type="button" class="text-left text-sm text-danger hover:underline" @click="onRemoveAvatar">
            Avatarı kaldır
          </button>
        </div>
      </div>

      <BaseInput v-model="username" label="Kullanıcı adı" :hint="USERNAME_HINT" :error="usernameError || undefined" />
      <BaseInput v-model="displayName" label="Görünen ad" :maxlength="50" />
      <BaseTextarea v-model="bio" label="Biyografi" :maxlength="300" />
    </div>
    <template #footer>
      <BaseButton variant="secondary" @click="open = false">Vazgeç</BaseButton>
      <BaseButton :loading="updateMe.isPending.value || uploadAvatar.isPending.value" @click="save">Kaydet</BaseButton>
    </template>
  </BaseModal>
</template>
