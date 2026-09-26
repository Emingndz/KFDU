<script setup lang="ts">
import { computed, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { MessageCircle } from 'lucide-vue-next'
import { toast } from 'vue-sonner'
import type { ReviewOut } from '@/types'
import { useLikeActivity, useUnlikeActivity } from '@/api/social'
import { useAuthStore } from '@/stores/auth'
import { relativeTime } from '@/utils/format'
import BaseAvatar from '@/components/ui/BaseAvatar.vue'
import RatingDisplay from '@/components/content/RatingDisplay.vue'
import LikeButton from '@/components/content/LikeButton.vue'

const props = defineProps<{ review: ReviewOut }>()

const auth = useAuthStore()
const router = useRouter()

const revealSpoiler = ref(false)
const liked = ref(props.review.liked_by_me)
const likesCount = ref(props.review.likes_count)
const likePending = ref(false)

const likeMutation = useLikeActivity()
const unlikeMutation = useUnlikeActivity()

async function toggleLike(next: boolean) {
  if (!props.review.activity_id || likePending.value) return
  if (!auth.isAuthenticated) {
    toast.info('Bunun için giriş yapmalısın')
    void router.push({ path: '/giris', query: { redirect: router.currentRoute.value.fullPath } })
    return
  }
  likePending.value = true
  liked.value = next
  likesCount.value += next ? 1 : -1
  try {
    if (next) await likeMutation.mutateAsync(props.review.activity_id)
    else await unlikeMutation.mutateAsync(props.review.activity_id)
  } catch {
    liked.value = !next
    likesCount.value += next ? -1 : 1
    toast.error('Bir şeyler ters gitti')
  } finally {
    likePending.value = false
  }
}

const displayName = computed(() => props.review.author.display_name || props.review.author.username)
</script>

<template>
  <article class="flex flex-col gap-2 rounded-card border border-border p-4">
    <div class="flex items-start gap-3">
      <RouterLink :to="`/u/${review.author.username}`">
        <BaseAvatar :name="displayName" :src="review.author.avatar_url" size="sm" />
      </RouterLink>
      <div class="min-w-0 flex-1">
        <div class="flex flex-wrap items-center gap-2">
          <RouterLink :to="`/u/${review.author.username}`" class="text-sm font-medium text-fg hover:underline">
            {{ displayName }}
          </RouterLink>
          <RatingDisplay v-if="review.rating" :rating="review.rating" size="sm" />
        </div>
        <p class="text-xs text-muted">
          {{ relativeTime(review.created_at) }}
          <span v-if="review.is_edited">· düzenlendi</span>
        </p>
      </div>
    </div>

    <div class="relative">
      <p class="text-sm whitespace-pre-wrap text-fg" :class="{ 'blur-sm select-none': review.has_spoiler && !revealSpoiler }">
        {{ review.excerpt }}
        <RouterLink v-if="review.is_truncated" :to="`/inceleme/${review.id}`" class="font-medium text-brand-600 hover:underline">
          …devamını oku
        </RouterLink>
      </p>
      <button
        v-if="review.has_spoiler && !revealSpoiler"
        type="button"
        class="absolute inset-0 flex items-center justify-center text-sm font-medium text-fg"
        @click="revealSpoiler = true"
      >
        Spoiler'ı göster
      </button>
    </div>

    <div class="flex items-center gap-4">
      <LikeButton :model-value="liked" :count="likesCount" :disabled="!review.activity_id" @update:model-value="toggleLike" />
      <RouterLink :to="`/inceleme/${review.id}`" class="flex items-center gap-1 text-sm text-muted hover:text-fg">
        <MessageCircle class="size-4" />
        {{ review.comments_count }}
      </RouterLink>
    </div>
  </article>
</template>
