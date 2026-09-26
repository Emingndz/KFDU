<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useIntersectionObserver } from '@vueuse/core'
import type { FeedScope } from '@/api/social'
import { useFeed } from '@/api/social'
import { useSuggestions } from '@/api/users'
import { useTrending } from '@/api/catalog'
import { useFollowToggle } from '@/composables/useFollowToggle'
import ActivityCard from '@/components/content/ActivityCard.vue'
import PosterCard from '@/components/content/PosterCard.vue'
import UserCard from '@/components/users/UserCard.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseSkeleton from '@/components/ui/BaseSkeleton.vue'
import ErrorState from '@/components/ui/ErrorState.vue'
import EmptyState from '@/components/ui/EmptyState.vue'

const scope = ref<FeedScope>('following')
const autoSwitched = ref(false)

const feed = useFeed(scope)

const items = computed(() => feed.data.value?.pages.flatMap((p) => p.items) ?? [])

watch(
  () => feed.data.value,
  (data) => {
    if (!autoSwitched.value && scope.value === 'following' && data && data.pages[0]?.items.length === 0) {
      autoSwitched.value = true
      scope.value = 'global'
    }
  },
)

function selectScope(next: FeedScope) {
  autoSwitched.value = true
  scope.value = next
}

const sentinelRef = ref<HTMLElement | null>(null)
useIntersectionObserver(
  sentinelRef,
  ([entry]) => {
    if (entry?.isIntersecting && feed.hasNextPage.value && !feed.isFetchingNextPage.value) {
      void feed.fetchNextPage()
    }
  },
  { rootMargin: '400px' },
)

const suggestions = useSuggestions(5)
const trending = useTrending('book')
const followToggle = useFollowToggle()
</script>

<template>
  <div class="grid gap-6 py-6 lg:grid-cols-[1fr_320px]">
    <div class="flex flex-col gap-4">
      <div class="flex gap-1 rounded-lg bg-surface-2 p-1">
        <button
          type="button"
          class="flex-1 rounded-md px-3 py-2 text-sm font-medium transition"
          :class="scope === 'following' ? 'bg-surface text-fg shadow-sm' : 'text-muted hover:text-fg'"
          @click="selectScope('following')"
        >
          Takip Ettiklerim
        </button>
        <button
          type="button"
          class="flex-1 rounded-md px-3 py-2 text-sm font-medium transition"
          :class="scope === 'global' ? 'bg-surface text-fg shadow-sm' : 'text-muted hover:text-fg'"
          @click="selectScope('global')"
        >
          Herkes
        </button>
      </div>

      <div v-if="scope === 'following' && !feed.isPending.value" class="rounded-card border border-border p-4">
        <p class="text-sm font-medium text-fg">Arkadaşlarını bul</p>
        <p class="mt-1 text-sm text-muted">Takip ettiğin kişilerin aktivitelerini burada göreceksin.</p>
        <BaseButton size="sm" class="mt-2" to="/kesfet">Kullanıcı ara</BaseButton>
      </div>

      <div v-if="feed.isPending.value" class="flex flex-col gap-4">
        <BaseSkeleton v-for="i in 3" :key="i" class="h-40 w-full" rounded="lg" />
      </div>
      <ErrorState v-else-if="feed.isError.value" message="Akış yüklenemedi." @retry="() => feed.refetch()" />
      <EmptyState
        v-else-if="items.length === 0"
        :title="scope === 'following' ? 'Henüz kimseyi takip etmiyorsun' : 'Henüz hiç aktivite yok'"
        message="Bir film, dizi veya kitap puanlayıp inceleme yazarak başlayabilirsin."
      />
      <template v-else>
        <ActivityCard v-for="activity in items" :key="activity.id" :activity="activity" />
        <div ref="sentinelRef" />
        <div v-if="feed.isFetchingNextPage.value" class="flex justify-center py-4">
          <BaseSkeleton class="h-40 w-full" rounded="lg" />
        </div>
        <BaseButton
          v-else-if="feed.hasNextPage.value"
          variant="secondary"
          @click="feed.fetchNextPage()"
        >
          Daha fazla yükle
        </BaseButton>
        <p v-else class="py-4 text-center text-sm text-muted">Hepsi bu kadar 🎉</p>
      </template>
    </div>

    <aside class="hidden flex-col gap-6 lg:flex">
      <section class="flex flex-col gap-3 rounded-card border border-border p-4">
        <h2 class="text-sm font-semibold text-fg">Kimi takip etmeli?</h2>
        <BaseSkeleton v-if="suggestions.isPending.value" class="h-32 w-full" />
        <div v-else class="flex flex-col gap-2">
          <UserCard
            v-for="user in suggestions.data.value ?? []"
            :key="user.username"
            :user="user"
            :is-following="followToggle.isFollowing(user.username)"
            :follow-pending="followToggle.isPending(user.username)"
            @toggle-follow="followToggle.toggle(user.username)"
          />
        </div>
      </section>

      <section class="flex flex-col gap-3 rounded-card border border-border p-4">
        <h2 class="text-sm font-semibold text-fg">Trend Kitaplar</h2>
        <BaseSkeleton v-if="trending.isPending.value" class="h-32 w-full" />
        <div v-else class="flex flex-wrap gap-3">
          <PosterCard v-for="item in (trending.data.value ?? []).slice(0, 4)" :key="item.external_id" :content="item" size="sm" />
        </div>
      </section>
    </aside>
  </div>
</template>
