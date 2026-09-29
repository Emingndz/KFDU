<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useQueryClient } from '@tanstack/vue-query'
import { toast } from 'vue-sonner'
import { ApiError } from '@/api/client'
import { useLikeActivity, useReviewDetail, useUnlikeActivity } from '@/api/social'
import { deleteReviewRequest, updateReviewRequest } from '@/api/library'
import { useAuthStore } from '@/stores/auth'
import { useConfirm } from '@/composables/useConfirm'
import { contentPath, typeLabel } from '@/utils/content'
import { relativeTime } from '@/utils/format'
import BaseAvatar from '@/components/ui/BaseAvatar.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseSkeleton from '@/components/ui/BaseSkeleton.vue'
import ErrorState from '@/components/ui/ErrorState.vue'
import SafeImage from '@/components/ui/SafeImage.vue'
import RatingDisplay from '@/components/content/RatingDisplay.vue'
import LikeButton from '@/components/content/LikeButton.vue'
import CommentThread from '@/components/content/CommentThread.vue'

const props = defineProps<{ id: string }>()
const reviewId = computed(() => Number(props.id))

const router = useRouter()
const auth = useAuthStore()
const queryClient = useQueryClient()
const { confirm } = useConfirm()

const review = useReviewDetail(reviewId)

const is404 = computed(() => review.isError.value && review.error.value instanceof ApiError && review.error.value.status === 404)
const isOwner = computed(() => Boolean(auth.me && review.data.value && auth.me.id === review.data.value.author.id))
const authorName = computed(() => review.data.value && (review.data.value.author.display_name || review.data.value.author.username))

const revealSpoiler = ref(false)
const liked = ref(false)
const likesCount = ref(0)
const likePending = ref(false)

watch(
  () => review.data.value,
  (r) => {
    if (r) {
      liked.value = r.liked_by_me
      likesCount.value = r.likes_count
    }
    if (r) document.title = `${authorName.value}'in incelemesi · ${r.content.title} · KFDU`
  },
  { immediate: true },
)

const likeMutation = useLikeActivity()
const unlikeMutation = useUnlikeActivity()

async function toggleLike(next: boolean) {
  const activityId = review.data.value?.activity_id
  if (!activityId || likePending.value) return
  if (!auth.isAuthenticated) {
    toast.info('Bunun için giriş yapmalısın')
    void router.push({ path: '/giris', query: { redirect: router.currentRoute.value.fullPath } })
    return
  }
  likePending.value = true
  liked.value = next
  likesCount.value += next ? 1 : -1
  try {
    if (next) await likeMutation.mutateAsync(activityId)
    else await unlikeMutation.mutateAsync(activityId)
  } catch {
    liked.value = !next
    likesCount.value += next ? -1 : 1
    toast.error('Bir şeyler ters gitti')
  } finally {
    likePending.value = false
  }
}

async function share() {
  try {
    await navigator.clipboard.writeText(window.location.href)
    toast.success('Bağlantı kopyalandı')
  } catch {
    toast.error('Bağlantı kopyalanamadı')
  }
}

const editing = ref(false)
const editBody = ref('')
const editSpoiler = ref(false)
const savingEdit = ref(false)
const deletingReview = ref(false)

function startEdit() {
  if (!review.data.value) return
  editBody.value = review.data.value.body
  editSpoiler.value = review.data.value.has_spoiler
  editing.value = true
}

async function saveEdit() {
  if (!review.data.value) return
  const body = editBody.value.trim()
  if (body.length < 3) {
    toast.error('İnceleme en az 3 karakter olmalı')
    return
  }
  savingEdit.value = true
  try {
    await updateReviewRequest(review.data.value.id, { body, has_spoiler: editSpoiler.value })
    await queryClient.invalidateQueries({ queryKey: ['review', reviewId.value] })
    editing.value = false
    toast.success('İnceleme güncellendi')
  } catch (error) {
    toast.error(error instanceof ApiError ? error.message : 'İnceleme güncellenemedi')
  } finally {
    savingEdit.value = false
  }
}

async function removeReview() {
  if (!review.data.value) return
  const ok = await confirm({ title: 'İncelemeyi sil', message: 'Bu işlem geri alınamaz.', confirmText: 'Evet, sil', danger: true })
  if (!ok) return
  deletingReview.value = true
  try {
    const content = review.data.value.content
    await deleteReviewRequest(review.data.value.id)
    toast.success('İnceleme silindi')
    void router.push(contentPath(content.type, content.external_id))
  } catch {
    toast.error('İnceleme silinemedi')
    deletingReview.value = false
  }
}
</script>

<template>
  <div v-if="review.isPending.value" class="flex flex-col gap-4 py-6">
    <BaseSkeleton class="h-20 w-full" rounded="lg" />
    <BaseSkeleton class="h-24 w-full" />
  </div>

  <div v-else-if="is404" class="flex flex-col items-center gap-3 py-24 text-center">
    <p class="text-lg font-semibold text-fg">Bu inceleme bulunamadı</p>
    <BaseButton @click="router.push('/kesfet')">Keşfet'e dön</BaseButton>
  </div>

  <ErrorState v-else-if="review.isError.value" message="İnceleme yüklenemedi." @retry="() => review.refetch()" />

  <div v-else-if="review.data.value" class="flex flex-col gap-6 py-6">
    <RouterLink
      :to="contentPath(review.data.value.content.type, review.data.value.content.external_id)"
      class="flex items-center gap-3 rounded-card border border-border p-3 hover:bg-surface-2"
    >
      <SafeImage
        :src="review.data.value.content.poster_url"
        :alt="review.data.value.content.title"
        class="aspect-[2/3] w-12 rounded object-cover"
      />
      <div>
        <p class="text-xs text-muted">{{ typeLabel(review.data.value.content.type) }}</p>
        <p class="font-medium text-fg">{{ review.data.value.content.title }} ({{ review.data.value.content.year }})</p>
      </div>
    </RouterLink>

    <div class="flex flex-col gap-3">
      <div class="flex items-center gap-3">
        <RouterLink :to="`/u/${review.data.value.author.username}`">
          <BaseAvatar :name="authorName ?? ''" :src="review.data.value.author.avatar_url" />
        </RouterLink>
        <div>
          <RouterLink :to="`/u/${review.data.value.author.username}`" class="font-medium text-fg hover:underline">
            {{ authorName }}
          </RouterLink>
          <p class="text-xs text-muted">
            {{ relativeTime(review.data.value.created_at) }}
            <span v-if="review.data.value.is_edited">· düzenlendi</span>
          </p>
        </div>
        <RatingDisplay v-if="review.data.value.rating" :rating="review.data.value.rating" class="ml-auto" />
      </div>

      <div v-if="editing" class="flex flex-col gap-2">
        <textarea
          v-model="editBody"
          rows="6"
          maxlength="5000"
          class="w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm text-fg focus-visible:outline-2 focus-visible:outline-brand-500"
        />
        <label class="flex items-center gap-2 text-sm text-fg">
          <input v-model="editSpoiler" type="checkbox" class="size-4 accent-brand-500" />
          Spoiler içeriyor
        </label>
        <div class="flex gap-2">
          <BaseButton :loading="savingEdit" @click="saveEdit">Kaydet</BaseButton>
          <BaseButton variant="ghost" @click="editing = false">Vazgeç</BaseButton>
        </div>
      </div>
      <div v-else class="relative">
        <p class="text-sm whitespace-pre-wrap text-fg" :class="{ 'blur-sm select-none': review.data.value.has_spoiler && !revealSpoiler }">
          {{ review.data.value.body }}
        </p>
        <button
          v-if="review.data.value.has_spoiler && !revealSpoiler"
          type="button"
          class="absolute inset-0 flex items-center justify-center text-sm font-medium text-fg"
          @click="revealSpoiler = true"
        >
          Spoiler'ı göster
        </button>
      </div>

      <div class="flex items-center gap-4">
        <LikeButton :model-value="liked" :count="likesCount" :disabled="!review.data.value.activity_id" @update:model-value="toggleLike" />
        <BaseButton variant="ghost" size="sm" @click="share">Paylaş</BaseButton>
        <template v-if="isOwner && !editing">
          <BaseButton variant="ghost" size="sm" @click="startEdit">Düzenle</BaseButton>
          <BaseButton variant="danger" size="sm" :loading="deletingReview" @click="removeReview">Sil</BaseButton>
        </template>
      </div>
    </div>

    <section v-if="review.data.value.activity_id" class="flex flex-col gap-3">
      <h2 class="text-lg font-semibold text-fg">Yorumlar</h2>
      <CommentThread :activity-id="review.data.value.activity_id" />
    </section>
  </div>
</template>
