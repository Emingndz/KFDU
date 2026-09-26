<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { toast } from 'vue-sonner'
import { ApiError } from '@/api/client'
import type { CatalogContentType } from '@/api/catalog'
import { useCreateReview, useDeleteReview, useUpdateReview } from '@/api/library'
import { useReviewDetail } from '@/api/social'
import { useConfirm } from '@/composables/useConfirm'
import { formatDate } from '@/utils/format'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseTextarea from '@/components/ui/BaseTextarea.vue'
import BaseSpinner from '@/components/ui/BaseSpinner.vue'

const props = defineProps<{ type: CatalogContentType; externalId: string; reviewId: number | null }>()

const { confirm } = useConfirm()

const editing = ref(false)
const body = ref('')
const hasSpoiler = ref(false)
const formError = ref('')

const existing = useReviewDetail(() => props.reviewId)
const createReview = useCreateReview()
const updateReview = useUpdateReview(props.type, props.externalId)
const deleteReview = useDeleteReview(props.type, props.externalId)

watch(
  () => existing.data.value,
  (review) => {
    if (review && !editing.value) {
      body.value = review.body
      hasSpoiler.value = review.has_spoiler
    }
  },
  { immediate: true },
)

const isWriting = computed(() => !props.reviewId || editing.value)

function startEdit() {
  if (existing.data.value) {
    body.value = existing.data.value.body
    hasSpoiler.value = existing.data.value.has_spoiler
  }
  editing.value = true
  formError.value = ''
}

function cancelEdit() {
  editing.value = false
  formError.value = ''
}

async function submit() {
  formError.value = ''
  if (body.value.trim().length < 3) {
    formError.value = 'İnceleme en az 3 karakter olmalı'
    return
  }
  try {
    if (props.reviewId) {
      await updateReview.mutateAsync({ reviewId: props.reviewId, payload: { body: body.value, has_spoiler: hasSpoiler.value } })
      toast.success('İnceleme güncellendi')
    } else {
      await createReview.mutateAsync({ type: props.type, external_id: props.externalId, body: body.value, has_spoiler: hasSpoiler.value })
      toast.success('İnceleme eklendi')
    }
    editing.value = false
  } catch (error) {
    formError.value = error instanceof ApiError ? error.message : 'İnceleme kaydedilemedi'
  }
}

async function remove() {
  if (!props.reviewId) return
  const ok = await confirm({ title: 'İncelemeyi sil', message: 'Bu işlem geri alınamaz.', confirmText: 'Evet, sil', danger: true })
  if (!ok) return
  try {
    await deleteReview.mutateAsync(props.reviewId)
    body.value = ''
    hasSpoiler.value = false
    toast.success('İnceleme silindi')
  } catch {
    toast.error('İnceleme silinemedi')
  }
}
</script>

<template>
  <div class="flex flex-col gap-3 rounded-card border border-border p-4">
    <div v-if="existing.isPending.value && reviewId" class="flex justify-center py-4"><BaseSpinner /></div>

    <template v-else-if="isWriting">
      <p v-if="formError" role="alert" class="rounded-lg bg-danger/10 px-3 py-2 text-sm text-danger">{{ formError }}</p>
      <BaseTextarea v-model="body" label="İncelemen" :maxlength="5000" hint="En az 3 karakter" />
      <label class="flex items-center gap-2 text-sm text-fg">
        <input v-model="hasSpoiler" type="checkbox" class="size-4 accent-brand-500" />
        Spoiler içeriyor
      </label>
      <div class="flex gap-2">
        <BaseButton :loading="createReview.isPending.value || updateReview.isPending.value" @click="submit">
          {{ reviewId ? 'Kaydet' : 'Gönder' }}
        </BaseButton>
        <BaseButton v-if="reviewId" variant="ghost" @click="cancelEdit">Vazgeç</BaseButton>
      </div>
    </template>

    <template v-else-if="existing.data.value">
      <div class="flex items-center justify-between">
        <p class="text-xs text-muted">Senin incelemen · {{ formatDate(existing.data.value.created_at) }}</p>
        <div class="flex gap-2">
          <BaseButton size="sm" variant="secondary" @click="startEdit">Düzenle</BaseButton>
          <BaseButton size="sm" variant="danger" :loading="deleteReview.isPending.value" @click="remove">Sil</BaseButton>
        </div>
      </div>
      <p v-if="existing.data.value.has_spoiler" class="text-sm text-warning">⚠ Bu inceleme spoiler içeriyor</p>
      <p class="text-sm whitespace-pre-wrap text-fg">{{ existing.data.value.body }}</p>
    </template>
  </div>
</template>
