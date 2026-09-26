<script setup lang="ts">
import { computed } from 'vue'
import { useFollowers, useFollowing } from '@/api/users'
import { useFollowToggle } from '@/composables/useFollowToggle'
import BaseModal from '@/components/ui/BaseModal.vue'
import UserCard from '@/components/users/UserCard.vue'
import BaseSpinner from '@/components/ui/BaseSpinner.vue'

const props = defineProps<{ username: string; mode: 'followers' | 'following' }>()
const open = defineModel<boolean>({ default: false })

const followersQuery = useFollowers(
  () => props.username,
  () => open.value && props.mode === 'followers',
)
const followingQuery = useFollowing(
  () => props.username,
  () => open.value && props.mode === 'following',
)
const activeQuery = computed(() => (props.mode === 'followers' ? followersQuery : followingQuery))
const items = computed(() => activeQuery.value.data.value?.pages.flatMap((p) => p.items) ?? [])

const followToggle = useFollowToggle()
</script>

<template>
  <BaseModal v-model="open" :title="mode === 'followers' ? 'Takipçiler' : 'Takip edilenler'">
    <div v-if="activeQuery.isPending.value" class="flex justify-center py-6"><BaseSpinner /></div>
    <p v-else-if="items.length === 0" class="py-6 text-center text-sm text-muted">Henüz kimse yok.</p>
    <div v-else class="flex max-h-96 flex-col gap-2 overflow-y-auto">
      <UserCard
        v-for="user in items"
        :key="user.username"
        :user="user"
        :is-following="user.is_following || followToggle.isFollowing(user.username)"
        :follow-pending="followToggle.isPending(user.username)"
        @toggle-follow="followToggle.toggle(user.username)"
      />
    </div>
  </BaseModal>
</template>
