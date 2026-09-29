<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { useGenres } from '@/api/catalog'
import { followUserRequest, unfollowUserRequest, useSuggestions, useUpdateMe } from '@/api/users'
import BaseAvatar from '@/components/ui/BaseAvatar.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseSkeleton from '@/components/ui/BaseSkeleton.vue'
import ErrorState from '@/components/ui/ErrorState.vue'
import GenreChipPicker from '@/components/users/GenreChipPicker.vue'

const router = useRouter()

const step = ref<1 | 2 | 3>(1)
const selectedGenres = ref(new Set<string>())

function toggleGenre(key: string) {
  if (selectedGenres.value.has(key)) selectedGenres.value.delete(key)
  else selectedGenres.value.add(key)
}

const movieGenres = useGenres('movie')
const tvGenres = useGenres('tv')
const bookGenres = useGenres('book')

const movieTvGenres = computed(() => {
  const byKey = new Map<string, { key: string; label: string }>()
  for (const g of movieGenres.data.value ?? []) byKey.set(g.key, g)
  for (const g of tvGenres.data.value ?? []) byKey.set(g.key, g)
  return [...byKey.values()]
})

const step1Loading = computed(() => movieGenres.isPending.value || tvGenres.isPending.value)
const step1Error = computed(() => movieGenres.isError.value || tvGenres.isError.value)
const step1Count = computed(() => movieTvGenres.value.filter((g) => selectedGenres.value.has(g.key)).length)
const canAdvanceStep1 = computed(() => step1Count.value >= 3)

const step2Count = computed(() => (bookGenres.data.value ?? []).filter((g) => selectedGenres.value.has(g.key)).length)

const suggestions = useSuggestions(10)
const following = ref<Record<string, boolean>>({})
const followPending = ref<Record<string, boolean>>({})

async function toggleFollow(username: string) {
  if (followPending.value[username]) return
  followPending.value[username] = true
  try {
    if (following.value[username]) {
      await unfollowUserRequest(username)
      following.value[username] = false
    } else {
      await followUserRequest(username)
      following.value[username] = true
    }
  } catch {
    toast.error('Bir şeyler ters gitti, tekrar dene')
  } finally {
    followPending.value[username] = false
  }
}

const updateMe = useUpdateMe()
const finishing = ref(false)

async function finish() {
  if (finishing.value) return
  finishing.value = true
  try {
    await updateMe.mutateAsync({ favorite_genres: [...selectedGenres.value] })
  } catch {
    toast.error('Tercihlerin kaydedilemedi ama devam edebilirsin')
  }
  await router.push('/')
}
</script>

<template>
  <div class="mx-auto flex max-w-lg flex-col gap-6 px-4 py-16">
    <div class="text-center">
      <h1 class="text-2xl font-bold text-fg">Hoş geldin</h1>
      <p class="mt-1 text-sm text-muted">Adım {{ step }}/3</p>
    </div>

    <section v-if="step === 1" class="flex flex-col gap-4">
      <p class="text-sm text-muted">Sevdiğin film/dizi türlerini seç (en az 3).</p>
      <ErrorState v-if="step1Error" message="Türler yüklenemedi." @retry="() => { movieGenres.refetch(); tvGenres.refetch() }" />
      <div v-else-if="step1Loading" class="flex flex-wrap gap-2">
        <BaseSkeleton v-for="i in 12" :key="i" class="h-8 w-20" rounded="full" />
      </div>
      <GenreChipPicker v-else :genres="movieTvGenres" :selected="selectedGenres" @toggle="toggleGenre" />
      <BaseButton class="w-full" :disabled="!canAdvanceStep1" @click="step = 2">
        İleri {{ canAdvanceStep1 ? '' : `(${step1Count}/3)` }}
      </BaseButton>
    </section>

    <section v-else-if="step === 2" class="flex flex-col gap-4">
      <p class="text-sm text-muted">Sevdiğin kitap türlerini seç (en az 2, istersen atla).</p>
      <div v-if="bookGenres.isPending.value" class="flex flex-wrap gap-2">
        <BaseSkeleton v-for="i in 10" :key="i" class="h-8 w-20" rounded="full" />
      </div>
      <ErrorState v-else-if="bookGenres.isError.value" message="Türler yüklenemedi." @retry="() => bookGenres.refetch()" />
      <GenreChipPicker v-else :genres="bookGenres.data.value ?? []" :selected="selectedGenres" @toggle="toggleGenre" />
      <div class="flex gap-3">
        <BaseButton variant="ghost" class="flex-1" @click="step = 3">Atla</BaseButton>
        <BaseButton class="flex-1" :disabled="step2Count < 2" @click="step = 3">İleri</BaseButton>
      </div>
    </section>

    <section v-else class="flex flex-col gap-4">
      <p class="text-sm text-muted">Takip edebileceğin bazı kullanıcılar:</p>
      <div v-if="suggestions.isPending.value" class="flex flex-col gap-3">
        <BaseSkeleton v-for="i in 4" :key="i" class="h-14 w-full" rounded="lg" />
      </div>
      <ErrorState
        v-else-if="suggestions.isError.value"
        message="Öneriler yüklenemedi."
        @retry="() => suggestions.refetch()"
      />
      <p v-else-if="(suggestions.data.value ?? []).length === 0" class="text-sm text-muted">
        Şimdilik önerecek kimse yok, sonra profillerden takip edebilirsin.
      </p>
      <ul v-else class="flex flex-col gap-2">
        <li
          v-for="person in suggestions.data.value"
          :key="person.username"
          class="flex items-center gap-3 rounded-lg border border-border p-3"
        >
          <BaseAvatar :name="person.display_name || person.username" :src="person.avatar_url" size="sm" />
          <div class="min-w-0 flex-1">
            <p class="truncate text-sm font-medium text-fg">{{ person.display_name || person.username }}</p>
            <p class="truncate text-xs text-muted">@{{ person.username }}</p>
          </div>
          <BaseButton
            size="sm"
            :variant="following[person.username] ? 'secondary' : 'primary'"
            :loading="followPending[person.username]"
            @click="toggleFollow(person.username)"
          >
            {{ following[person.username] ? 'Takip ediliyor' : 'Takip et' }}
          </BaseButton>
        </li>
      </ul>
      <BaseButton class="w-full" :loading="finishing" @click="finish">Bitir</BaseButton>
    </section>
  </div>
</template>
