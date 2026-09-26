<script setup lang="ts">
import type { ProfileOut, ProfileSummaryOut } from '@/types'
import { formatDate } from '@/utils/format'
import BaseAvatar from '@/components/ui/BaseAvatar.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import FollowButton from '@/components/users/FollowButton.vue'

defineProps<{
  profile: ProfileOut
  summary?: ProfileSummaryOut
  followPending?: boolean
}>()
defineEmits<{
  editProfile: []
  newList: []
  showFollowers: []
  showFollowing: []
  toggleFollow: []
}>()
</script>

<template>
  <div class="flex flex-col gap-4 sm:flex-row sm:items-start">
    <BaseAvatar :name="profile.display_name || profile.username" :src="profile.avatar_url" size="xl" />
    <div class="flex-1">
      <div class="flex flex-wrap items-center gap-2">
        <h1 class="text-xl font-bold text-fg">{{ profile.display_name || profile.username }}</h1>
        <span v-if="profile.follows_me" class="rounded-full bg-surface-2 px-2 py-0.5 text-xs text-muted">Seni takip ediyor</span>
      </div>
      <p class="text-sm text-muted">@{{ profile.username }}</p>
      <p v-if="profile.bio" class="mt-2 text-sm text-fg">{{ profile.bio }}</p>
      <p class="mt-1 text-xs text-muted">{{ formatDate(profile.created_at) }} tarihinde katıldı</p>

      <div class="mt-3 flex flex-wrap gap-4 text-sm">
        <button type="button" class="hover:underline" @click="$emit('showFollowers')">
          <span class="font-semibold text-fg">{{ profile.followers_count }}</span> <span class="text-muted">Takipçi</span>
        </button>
        <button type="button" class="hover:underline" @click="$emit('showFollowing')">
          <span class="font-semibold text-fg">{{ profile.following_count }}</span> <span class="text-muted">Takip</span>
        </button>
        <template v-if="summary">
          <span><span class="font-semibold text-fg">{{ summary.movies_completed }}</span> <span class="text-muted">Film</span></span>
          <span><span class="font-semibold text-fg">{{ summary.tv_completed }}</span> <span class="text-muted">Dizi</span></span>
          <span><span class="font-semibold text-fg">{{ summary.books_completed }}</span> <span class="text-muted">Kitap</span></span>
          <span><span class="font-semibold text-fg">{{ summary.reviews }}</span> <span class="text-muted">İnceleme</span></span>
        </template>
      </div>

      <div class="mt-3 flex gap-2">
        <template v-if="profile.is_me">
          <BaseButton variant="secondary" size="sm" @click="$emit('editProfile')">Profili Düzenle</BaseButton>
          <BaseButton variant="secondary" size="sm" @click="$emit('newList')">Yeni Liste</BaseButton>
        </template>
        <FollowButton v-else :is-following="profile.is_following" :pending="followPending" @toggle="$emit('toggleFollow')" />
      </div>
    </div>
  </div>
</template>
