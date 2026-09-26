<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { ApiError } from '@/api/client'
import { useCreateList } from '@/api/lists'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseTextarea from '@/components/ui/BaseTextarea.vue'
import BaseButton from '@/components/ui/BaseButton.vue'

const open = defineModel<boolean>({ default: false })
const router = useRouter()

const title = ref('')
const description = ref('')
const isPublic = ref(true)

const createList = useCreateList()

async function submit() {
  if (!title.value.trim()) return
  try {
    const list = await createList.mutateAsync({
      title: title.value.trim(),
      description: description.value.trim() || null,
      is_public: isPublic.value,
    })
    toast.success('Liste oluşturuldu')
    title.value = ''
    description.value = ''
    isPublic.value = true
    open.value = false
    void router.push(`/liste/${list.id}`)
  } catch (error) {
    toast.error(error instanceof ApiError ? error.message : 'Liste oluşturulamadı')
  }
}
</script>

<template>
  <BaseModal v-model="open" title="Yeni liste">
    <div class="flex flex-col gap-4">
      <BaseInput v-model="title" label="Başlık" :maxlength="100" />
      <BaseTextarea v-model="description" label="Açıklama (isteğe bağlı)" :maxlength="500" />
      <label class="flex items-center gap-2 text-sm text-fg">
        <input v-model="isPublic" type="checkbox" class="size-4 accent-brand-500" />
        Herkese açık
      </label>
    </div>
    <template #footer>
      <BaseButton variant="secondary" @click="open = false">Vazgeç</BaseButton>
      <BaseButton :loading="createList.isPending.value" :disabled="!title.trim()" @click="submit">Oluştur</BaseButton>
    </template>
  </BaseModal>
</template>
