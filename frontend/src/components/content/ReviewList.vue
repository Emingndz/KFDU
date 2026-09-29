<script setup lang="ts">
import { computed, ref } from 'vue'
import type { CatalogContentType } from '@/api/catalog'
import { useContentReviews } from '@/api/social'
import { useAuthStore } from '@/stores/auth'
import ReviewItem from './ReviewItem.vue'
import BaseSelect from '@/components/ui/BaseSelect.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseSpinner from '@/components/ui/BaseSpinner.vue'
import ErrorState from '@/components/ui/ErrorState.vue'

const props = defineProps<{ type: CatalogContentType; externalId: string }>()

const auth = useAuthStore()
const sort = ref<'new' | 'popular'>('new')

const reviews = useContentReviews(
  () => props.type,
  () => props.externalId,
  sort,
)

const items = computed(() => {
  const all = reviews.data.value?.pages.flatMap((p) => p.items) ?? []
  return auth.me ? all.filter((r) => r.author.id !== auth.me?.id) : all
})
</script>

<template>
  <section class="flex flex-col gap-3">
    <div class="flex items-center justify-between">
      <h2 class="text-lg font-semibold text-fg">İncelemeler</h2>
      <BaseSelect
        v-model="sort"
        aria-label="İncelemeleri sırala"
        :options="[
          { value: 'new', label: 'Yeni' },
          { value: 'popular', label: 'Popüler' },
        ]"
      />
    </div>

    <div v-if="reviews.isPending.value" class="flex justify-center py-6"><BaseSpinner /></div>
    <ErrorState v-else-if="reviews.isError.value" message="İncelemeler yüklenemedi." @retry="() => reviews.refetch()" />
    <p v-else-if="items.length === 0" class="text-sm text-muted">Henüz inceleme yok.</p>
    <div v-else class="flex flex-col gap-3">
      <ReviewItem v-for="review in items" :key="review.id" :review="review" />
      <BaseButton
        v-if="reviews.hasNextPage.value"
        variant="secondary"
        :loading="reviews.isFetchingNextPage.value"
        @click="reviews.fetchNextPage()"
      >
        Daha fazla
      </BaseButton>
    </div>
  </section>
</template>
