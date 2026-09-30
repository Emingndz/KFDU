<script setup lang="ts">
import { computed } from 'vue'
import { ApiError } from '@/api/client'
import { usePersonDetail } from '@/api/catalog'
import { contentPath } from '@/utils/content'
import BaseSkeleton from '@/components/ui/BaseSkeleton.vue'
import ErrorState from '@/components/ui/ErrorState.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import SafeImage from '@/components/ui/SafeImage.vue'
import CreditCard from '@/components/content/CreditCard.vue'

const props = defineProps<{ id: string }>()

const detail = usePersonDetail(() => props.id)
const is404 = computed(
  () => detail.isError.value && detail.error.value instanceof ApiError && detail.error.value.status === 404,
)
const directing = computed(() => detail.data.value?.directing ?? [])
const acting = computed(() => detail.data.value?.acting ?? [])
</script>

<template>
  <div v-if="detail.isPending.value" class="flex flex-col gap-6 py-6">
    <BaseSkeleton class="h-64 w-full" rounded="lg" />
  </div>

  <EmptyState v-else-if="is404" title="Bu kişi bulunamadı" />

  <ErrorState v-else-if="detail.isError.value" message="Kişi yüklenemedi." @retry="() => detail.refetch()" />

  <div v-else-if="detail.data.value" class="flex flex-col gap-8 py-6">
    <div class="flex flex-col gap-4 sm:flex-row">
      <SafeImage
        :src="detail.data.value.photo_url"
        :alt="detail.data.value.name"
        class="aspect-[2/3] w-40 shrink-0 rounded-card object-cover sm:w-48"
      />
      <div class="flex flex-1 flex-col gap-2">
        <h1 class="text-2xl font-bold text-fg">{{ detail.data.value.name }}</h1>
        <p v-if="detail.data.value.known_for" class="text-sm text-muted">{{ detail.data.value.known_for }}</p>
        <p v-if="detail.data.value.birthday || detail.data.value.birth_place" class="text-sm text-muted">
          <template v-if="detail.data.value.birthday">{{ detail.data.value.birthday }}</template>
          <template v-if="detail.data.value.birth_place"> · {{ detail.data.value.birth_place }}</template>
        </p>
        <p v-if="detail.data.value.biography" class="mt-2 line-clamp-6 text-sm whitespace-pre-wrap text-fg">
          {{ detail.data.value.biography }}
        </p>
      </div>
    </div>

    <section v-if="directing.length > 0" class="flex flex-col gap-3">
      <h2 class="text-lg font-semibold text-fg">Yönetmenlik</h2>
      <div class="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
        <CreditCard
          v-for="credit in directing"
          :key="`${credit.type}:${credit.external_id}`"
          :to="contentPath(credit.type, credit.external_id)"
          :title="credit.title"
          :poster-url="credit.poster_url"
          :year="credit.year"
        />
      </div>
    </section>

    <section v-if="acting.length > 0" class="flex flex-col gap-3">
      <h2 class="text-lg font-semibold text-fg">Oyunculuk</h2>
      <div class="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
        <CreditCard
          v-for="credit in acting"
          :key="`${credit.type}:${credit.external_id}`"
          :to="contentPath(credit.type, credit.external_id)"
          :title="credit.title"
          :poster-url="credit.poster_url"
          :year="credit.year"
        />
      </div>
    </section>

    <EmptyState v-if="directing.length === 0 && acting.length === 0" title="Kredi bulunamadı" />
  </div>
</template>
