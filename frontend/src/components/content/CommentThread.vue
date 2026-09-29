<script setup lang="ts">
import { computed, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { useAuthStore } from '@/stores/auth'
import { useAddComment, useComments, useDeleteComment, useUpdateComment } from '@/api/social'
import { useConfirm } from '@/composables/useConfirm'
import { relativeTime } from '@/utils/format'
import BaseAvatar from '@/components/ui/BaseAvatar.vue'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseSpinner from '@/components/ui/BaseSpinner.vue'

const props = withDefaults(defineProps<{ activityId: number; compact?: boolean }>(), { compact: false })
const emit = defineEmits<{ expand: [] }>()

const auth = useAuthStore()
const router = useRouter()
const { confirm } = useConfirm()

const comments = useComments(() => props.activityId)
const addComment = useAddComment(props.activityId)
const updateCommentMutation = useUpdateComment(props.activityId)
const deleteCommentMutation = useDeleteComment(props.activityId)

const allComments = computed(() => comments.data.value?.pages.flatMap((p) => p.items) ?? [])
const visibleComments = computed(() => (props.compact ? allComments.value.slice(-2) : allComments.value))

const newBody = ref('')
const pendingComments = ref<{ tempId: string; body: string }[]>([])
const editingId = ref<number | null>(null)
const editBody = ref('')
const deletingId = ref<number | null>(null)

function requireAuth(): boolean {
  if (auth.isAuthenticated) return true
  toast.info('Bunun için giriş yapmalısın')
  void router.push({ path: '/giris', query: { redirect: router.currentRoute.value.fullPath } })
  return false
}

async function submit() {
  const body = newBody.value.trim()
  if (!body || !requireAuth()) return
  newBody.value = ''
  const tempId = `pending-${Date.now()}`
  pendingComments.value.push({ tempId, body })
  try {
    await addComment.mutateAsync(body)
  } catch {
    toast.error('Yorum eklenemedi')
    newBody.value = body
  } finally {
    pendingComments.value = pendingComments.value.filter((c) => c.tempId !== tempId)
  }
}

function onKeydown(event: KeyboardEvent) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    void submit()
  }
}

function startEdit(commentId: number, body: string) {
  editingId.value = commentId
  editBody.value = body
}

function cancelEdit() {
  editingId.value = null
}

async function saveEdit(commentId: number) {
  const body = editBody.value.trim()
  if (!body) return
  try {
    await updateCommentMutation.mutateAsync({ commentId, body })
    editingId.value = null
  } catch {
    toast.error('Yorum güncellenemedi')
  }
}

async function remove(commentId: number) {
  const ok = await confirm({
    title: 'Yorumu sil',
    message: 'Bu işlem geri alınamaz.',
    confirmText: 'Evet, sil',
    danger: true,
  })
  if (!ok) return
  deletingId.value = commentId
  try {
    await deleteCommentMutation.mutateAsync(commentId)
  } catch {
    toast.error('Yorum silinemedi')
  } finally {
    deletingId.value = null
  }
}

function displayName(comment: { author: { display_name: string | null; username: string } }) {
  return comment.author.display_name || comment.author.username
}
</script>

<template>
  <div class="flex flex-col gap-3">
    <div v-if="comments.isPending.value" class="flex justify-center py-4"><BaseSpinner /></div>

    <template v-else>
      <BaseButton
        v-if="!compact && comments.hasNextPage.value"
        variant="ghost"
        size="sm"
        :loading="comments.isFetchingNextPage.value"
        @click="comments.fetchNextPage()"
      >
        Daha fazla yorum göster
      </BaseButton>

      <ul class="flex flex-col gap-3">
        <li v-for="comment in visibleComments" :key="comment.id" class="flex gap-2">
          <RouterLink :to="`/u/${comment.author.username}`" :aria-label="`${displayName(comment)} profili`">
            <BaseAvatar :name="displayName(comment)" :src="comment.author.avatar_url" size="sm" />
          </RouterLink>
          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-2">
              <RouterLink :to="`/u/${comment.author.username}`" class="text-sm font-medium text-fg hover:underline">
                {{ displayName(comment) }}
              </RouterLink>
              <span class="text-xs text-muted">
                {{ relativeTime(comment.created_at) }}
                <template v-if="comment.updated_at !== comment.created_at">· düzenlendi</template>
              </span>
            </div>

            <div v-if="editingId === comment.id" class="mt-1 flex flex-col gap-1.5">
              <textarea
                v-model="editBody"
                rows="2"
                maxlength="1000"
                class="w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm text-fg focus-visible:outline-2 focus-visible:outline-brand-500"
              />
              <div class="flex gap-2">
                <BaseButton size="sm" :loading="updateCommentMutation.isPending.value" @click="saveEdit(comment.id)">Kaydet</BaseButton>
                <BaseButton size="sm" variant="ghost" @click="cancelEdit">Vazgeç</BaseButton>
              </div>
            </div>
            <p v-else class="text-sm whitespace-pre-wrap text-fg">{{ comment.body }}</p>

            <div v-if="editingId !== comment.id && (comment.can_edit || comment.can_delete)" class="mt-1 flex gap-3 text-xs">
              <button v-if="comment.can_edit" type="button" class="text-muted hover:text-fg" @click="startEdit(comment.id, comment.body)">
                Düzenle
              </button>
              <button
                v-if="comment.can_delete"
                type="button"
                class="text-muted hover:text-danger"
                :disabled="deletingId === comment.id"
                @click="remove(comment.id)"
              >
                Sil
              </button>
            </div>
          </div>
        </li>
        <li v-for="pending in pendingComments" :key="pending.tempId" class="flex gap-2 opacity-60">
          <BaseAvatar :name="auth.me?.display_name || auth.me?.username || '?'" :src="auth.me?.avatar_url" size="sm" />
          <div class="min-w-0 flex-1">
            <p class="text-sm font-medium text-fg">{{ auth.me?.display_name || auth.me?.username }}</p>
            <p class="text-sm whitespace-pre-wrap text-fg">{{ pending.body }}</p>
            <p class="text-xs text-muted">Gönderiliyor…</p>
          </div>
        </li>
      </ul>

      <p v-if="allComments.length === 0 && pendingComments.length === 0" class="text-sm text-muted">Henüz yorum yok.</p>
      <button
        v-if="compact && allComments.length > visibleComments.length"
        type="button"
        class="w-fit text-sm font-medium text-link hover:underline"
        @click="emit('expand')"
      >
        Tüm yorumlar ({{ allComments.length }})
      </button>
    </template>

    <div class="flex flex-col gap-1.5">
      <textarea
        v-model="newBody"
        rows="2"
        maxlength="1000"
        placeholder="Bir yorum yaz…"
        class="w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm text-fg placeholder:text-muted focus-visible:outline-2 focus-visible:outline-brand-500"
        @keydown="onKeydown"
      />
      <div class="flex items-center justify-between">
        <span class="text-xs text-muted">{{ newBody.length }}/1000</span>
        <BaseButton size="sm" :disabled="!newBody.trim()" @click="submit">Gönder</BaseButton>
      </div>
    </div>
  </div>
</template>
