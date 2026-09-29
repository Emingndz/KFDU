<script setup lang="ts">
import { computed, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import type { ActivityOut } from '@/types'
import { useLike } from '@/api/social'
import { useAuthStore } from '@/stores/auth'
import { activityActionText } from '@/utils/activity'
import { contentPath, typeLabel } from '@/utils/content'
import { relativeTime } from '@/utils/format'
import BaseAvatar from '@/components/ui/BaseAvatar.vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import SafeImage from '@/components/ui/SafeImage.vue'
import RatingDisplay from '@/components/content/RatingDisplay.vue'
import LikeButton from '@/components/content/LikeButton.vue'
import CommentThread from '@/components/content/CommentThread.vue'

const props = defineProps<{ activity: ActivityOut }>()

const auth = useAuthStore()
const router = useRouter()
const likeMutation = useLike()

const authorName = computed(() => props.activity.actor.display_name || props.activity.actor.username)
const actionText = computed(() => activityActionText(props.activity))
const contentHref = computed(() =>
  props.activity.content ? contentPath(props.activity.content.type, props.activity.content.external_id) : null,
)

const STATUS_VARIANT: Record<string, 'success' | 'brand' | 'neutral' | 'danger'> = {
  completed: 'success',
  in_progress: 'brand',
  planned: 'neutral',
  dropped: 'danger',
}

const revealSpoiler = ref(false)

function toggleLike(next: boolean) {
  if (!auth.isAuthenticated) {
    toast.info('Bunun için giriş yapmalısın')
    void router.push({ path: '/giris', query: { redirect: router.currentRoute.value.fullPath } })
    return
  }
  likeMutation.mutate({ activityId: props.activity.id, liked: next })
}

async function share() {
  const url = contentHref.value ? `${window.location.origin}${contentHref.value}` : window.location.href
  try {
    await navigator.clipboard.writeText(url)
    toast.success('Bağlantı kopyalandı')
  } catch {
    toast.error('Bağlantı kopyalanamadı')
  }
}

const commentsMode = ref<'hidden' | 'compact' | 'full'>('hidden')
function toggleComments() {
  commentsMode.value = commentsMode.value === 'hidden' ? 'compact' : 'hidden'
}
</script>

<template>
  <article class="flex flex-col gap-3 rounded-card border border-border p-4">
    <div class="flex items-center gap-2">
      <RouterLink :to="`/u/${activity.actor.username}`" :aria-label="`${authorName} profili`">
        <BaseAvatar :name="authorName" :src="activity.actor.avatar_url" size="sm" />
      </RouterLink>
      <p class="text-sm text-fg">
        <RouterLink :to="`/u/${activity.actor.username}`" class="font-medium hover:underline">{{ authorName }}</RouterLink>
        {{ actionText }}
      </p>
      <span class="ml-auto text-xs whitespace-nowrap text-muted" :title="new Date(activity.created_at).toLocaleString('tr-TR')">
        {{ relativeTime(activity.created_at) }}
      </span>
    </div>

    <!-- rating -->
    <RouterLink v-if="activity.card_type === 'rating' && activity.content" :to="contentHref!" class="flex gap-3">
      <SafeImage :src="activity.content.poster_url" :alt="activity.content.title" class="aspect-[2/3] w-20 shrink-0 rounded-lg object-cover" />
      <div class="flex flex-col justify-center gap-1">
        <p class="font-medium text-fg">{{ activity.content.title }} ({{ activity.content.year }})</p>
        <RatingDisplay v-if="activity.rating" :rating="activity.rating" />
      </div>
    </RouterLink>

    <!-- review -->
    <div v-else-if="activity.card_type === 'review' && activity.content" class="flex gap-3">
      <RouterLink :to="contentHref!" class="shrink-0">
        <SafeImage :src="activity.content.poster_url" :alt="activity.content.title" class="aspect-[2/3] w-20 rounded-lg object-cover" />
      </RouterLink>
      <div class="flex min-w-0 flex-col gap-1">
        <RouterLink :to="contentHref!" class="font-medium text-fg hover:underline">{{ activity.content.title }}</RouterLink>
        <RatingDisplay v-if="activity.rating" :rating="activity.rating" size="sm" />
        <div v-if="activity.review" class="relative">
          <p class="text-sm whitespace-pre-wrap text-fg" :class="{ 'blur-sm select-none': activity.review.has_spoiler && !revealSpoiler }">
            {{ activity.review.excerpt }}
            <RouterLink v-if="activity.review.is_truncated" :to="`/inceleme/${activity.review.id}`" class="font-medium text-link hover:underline">
              …devamını oku
            </RouterLink>
          </p>
          <button
            v-if="activity.review.has_spoiler && !revealSpoiler"
            type="button"
            class="absolute inset-0 flex items-center justify-center text-sm font-medium text-fg"
            @click="revealSpoiler = true"
          >
            Spoiler'ı göster
          </button>
        </div>
      </div>
    </div>

    <!-- status -->
    <RouterLink v-else-if="activity.card_type === 'status' && activity.content" :to="contentHref!" class="flex items-center gap-3">
      <SafeImage :src="activity.content.poster_url" :alt="activity.content.title" class="aspect-[2/3] w-16 shrink-0 rounded-lg object-cover" />
      <p class="font-medium text-fg">{{ activity.content.title }}</p>
      <BaseBadge v-if="activity.status" :variant="STATUS_VARIANT[activity.status] ?? 'neutral'" class="ml-auto">
        {{ typeLabel(activity.content.type) }}
      </BaseBadge>
    </RouterLink>

    <!-- list_add -->
    <div v-else-if="activity.card_type === 'list_add' && activity.content" class="flex items-center gap-3">
      <RouterLink :to="contentHref!" class="shrink-0">
        <SafeImage :src="activity.content.poster_url" :alt="activity.content.title" class="aspect-[2/3] w-16 rounded-lg object-cover" />
      </RouterLink>
      <RouterLink :to="contentHref!" class="font-medium text-fg hover:underline">{{ activity.content.title }}</RouterLink>
      <RouterLink v-if="activity.list" :to="`/liste/${activity.list.id}`" class="text-sm text-link hover:underline">
        → {{ activity.list.title }}
      </RouterLink>
    </div>

    <!-- list_create -->
    <RouterLink v-else-if="activity.card_type === 'list_create' && activity.list" :to="`/liste/${activity.list.id}`" class="flex items-center gap-3">
      <div class="grid size-16 shrink-0 grid-cols-2 gap-0.5 overflow-hidden rounded-lg bg-surface-2">
        <SafeImage v-for="(cover, i) in activity.list.cover_urls.slice(0, 4)" :key="i" :src="cover" alt="" class="size-full object-cover" />
      </div>
      <div>
        <p class="font-medium text-fg">{{ activity.list.title }}</p>
        <p class="text-sm text-muted">{{ activity.list.item_count }} öğe</p>
      </div>
    </RouterLink>

    <div class="flex items-center gap-4 border-t border-border pt-3">
      <LikeButton :model-value="activity.liked_by_me" :count="activity.likes_count" @update:model-value="toggleLike" />
      <button type="button" class="text-sm text-muted hover:text-fg" @click="toggleComments">
        Yorum yap{{ activity.comments_count > 0 ? ` (${activity.comments_count})` : '' }}
      </button>
      <button type="button" class="text-sm text-muted hover:text-fg" @click="share">Paylaş</button>
    </div>

    <CommentThread
      v-if="commentsMode !== 'hidden'"
      :activity-id="activity.id"
      :compact="commentsMode === 'compact'"
      @expand="commentsMode = 'full'"
    />
  </article>
</template>
