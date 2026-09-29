<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { ApiError } from '@/api/client'
import { useCreateList, useUpdateList } from '@/api/lists'
import type { ListOut } from '@/types'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseTextarea from '@/components/ui/BaseTextarea.vue'
import BaseButton from '@/components/ui/BaseButton.vue'

const props = defineProps<{ list?: Pick<ListOut, 'id' | 'title' | 'description' | 'is_public'> | null }>()
const open = defineModel<boolean>({ default: false })
const router = useRouter()

const isEdit = computed(() => Boolean(props.list))

const title = ref('')
const description = ref('')
const isPublic = ref(true)

watch(open, (isOpen) => {
  if (!isOpen) return
  title.value = props.list?.title ?? ''
  description.value = props.list?.description ?? ''
  isPublic.value = props.list?.is_public ?? true
})

const createList = useCreateList()
const updateList = useUpdateList()
const pending = computed(() => createList.isPending.value || updateList.isPending.value)

async function submit() {
  const trimmedTitle = title.value.trim()
  if (!trimmedTitle) return
  try {
    if (props.list) {
      await updateList.mutateAsync({
        listId: props.list.id,
        payload: { title: trimmedTitle, description: description.value.trim() || null, is_public: isPublic.value },
      })
      toast.success('Liste güncellendi')
      open.value = false
    } else {
      const list = await createList.mutateAsync({
        title: trimmedTitle,
        description: description.value.trim() || null,
        is_public: isPublic.value,
      })
      toast.success('Liste oluşturuldu')
      open.value = false
      void router.push(`/liste/${list.id}`)
    }
  } catch (error) {
    toast.error(error instanceof ApiError ? error.message : isEdit.value ? 'Liste güncellenemedi' : 'Liste oluşturulamadı')
  }
}
</script>

<template>
  <BaseModal v-model="open" :title="isEdit ? 'Listeyi düzenle' : 'Yeni liste'">
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
      <BaseButton :loading="pending" :disabled="!title.trim()" @click="submit">{{ isEdit ? 'Kaydet' : 'Oluştur' }}</BaseButton>
    </template>
  </BaseModal>
</template>
