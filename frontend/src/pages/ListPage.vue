<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { ApiError } from '@/api/client'
import { useDeleteList, useListDetail, useRemoveListItem, useReorderListItems, useUpdateListItemNote } from '@/api/lists'
import { useAuthStore } from '@/stores/auth'
import { useConfirm } from '@/composables/useConfirm'
import type { ListItemOut } from '@/types'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import BaseSkeleton from '@/components/ui/BaseSkeleton.vue'
import ErrorState from '@/components/ui/ErrorState.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import SafeImage from '@/components/ui/SafeImage.vue'
import PosterCard from '@/components/content/PosterCard.vue'
import ListFormModal from '@/components/lists/ListFormModal.vue'

const props = defineProps<{ id: string }>()
const listId = computed(() => Number(props.id))

const router = useRouter()
const auth = useAuthStore()
const { confirm } = useConfirm()

const list = useListDetail(listId)

const is404 = computed(() => list.isError.value && list.error.value instanceof ApiError && list.error.value.status === 404)
const isOwner = computed(() => Boolean(auth.me && list.data.value && auth.me.id === list.data.value.owner.id))

watch(
  () => list.data.value,
  (l) => {
    if (l) document.title = `${l.title} · KFDU`
  },
)

async function share() {
  try {
    await navigator.clipboard.writeText(window.location.href)
    toast.success('Bağlantı kopyalandı')
  } catch {
    toast.error('Bağlantı kopyalanamadı')
  }
}

const editModalOpen = ref(false)

const deleteList = useDeleteList()
async function removeList() {
  if (!list.data.value) return
  const ok = await confirm({
    title: 'Listeyi sil',
    message: 'Bu işlem geri alınamaz, listedeki tüm öğeler kaldırılır.',
    confirmText: 'Evet, sil',
    danger: true,
  })
  if (!ok) return
  try {
    await deleteList.mutateAsync(listId.value)
    toast.success('Liste silindi')
    void router.push(auth.me ? `/u/${auth.me.username}` : '/kesfet')
  } catch {
    toast.error('Liste silinemedi')
  }
}

// Sıralama modu: sunucudan gelen sırayı yerel bir taslağa kopyalayıp ok tuşlarıyla düzenliyoruz,
// yalnızca "Sırayı kaydet" ile PUT /lists/{id}/order tetiklenir.
const reordering = ref(false)
const orderDraft = ref<ListItemOut[]>([])
const reorderMutation = useReorderListItems()

function startReorder() {
  orderDraft.value = [...(list.data.value?.items ?? [])]
  reordering.value = true
}
function cancelReorder() {
  reordering.value = false
}
function moveUp(index: number) {
  if (index === 0) return
  const arr = orderDraft.value
  ;[arr[index - 1], arr[index]] = [arr[index]!, arr[index - 1]!]
}
function moveDown(index: number) {
  if (index === orderDraft.value.length - 1) return
  const arr = orderDraft.value
  ;[arr[index], arr[index + 1]] = [arr[index + 1]!, arr[index]!]
}
async function saveOrder() {
  const contentIds = orderDraft.value.map((item) => item.content.id).filter((id): id is number => id != null)
  try {
    await reorderMutation.mutateAsync({ listId: listId.value, contentIds })
    toast.success('Sıralama kaydedildi')
    reordering.value = false
  } catch {
    toast.error('Sıralama kaydedilemedi')
  }
}

const displayItems = computed(() => (reordering.value ? orderDraft.value : (list.data.value?.items ?? [])))

const removeItemMutation = useRemoveListItem()
async function removeItem(contentId: number | null | undefined) {
  if (contentId == null) return
  try {
    await removeItemMutation.mutateAsync({ listId: listId.value, contentId })
    toast.success('Öğe listeden çıkarıldı')
  } catch {
    toast.error('Öğe çıkarılamadı')
  }
}

const editingNoteFor = ref<number | null>(null)
const noteDraft = ref('')
const updateNoteMutation = useUpdateListItemNote()

function startEditNote(item: ListItemOut) {
  if (item.content.id == null) return
  editingNoteFor.value = item.content.id
  noteDraft.value = item.note ?? ''
}
async function saveNote(contentId: number | null | undefined) {
  if (contentId == null) return
  try {
    await updateNoteMutation.mutateAsync({ listId: listId.value, contentId, note: noteDraft.value.trim() || null })
    editingNoteFor.value = null
  } catch {
    toast.error('Not kaydedilemedi')
  }
}
</script>

<template>
  <div v-if="list.isPending.value" class="flex flex-col gap-4 py-6">
    <BaseSkeleton class="aspect-[3/1] w-full" rounded="lg" />
    <BaseSkeleton class="h-8 w-1/2" />
    <BaseSkeleton class="h-4 w-1/3" />
  </div>

  <EmptyState v-else-if="is404" title="Bu liste bulunamadı" message="Liste kaldırılmış, gizli ya da hiç var olmamış olabilir." />

  <ErrorState v-else-if="list.isError.value" message="Liste yüklenemedi." @retry="() => list.refetch()" />

  <div v-else-if="list.data.value" class="flex flex-col gap-6 pb-24 py-6">
    <div class="overflow-hidden rounded-card">
      <div class="grid aspect-[3/1] grid-cols-4 gap-0.5 bg-gradient-to-br from-brand-500/30 to-brand-700/30">
        <SafeImage v-for="(cover, i) in list.data.value.cover_urls.slice(0, 4)" :key="i" :src="cover" alt="" class="size-full object-cover" />
      </div>
    </div>

    <div class="flex flex-col gap-2">
      <div class="flex flex-wrap items-center gap-2">
        <h1 class="text-2xl font-bold text-fg">{{ list.data.value.title }}</h1>
        <BaseBadge :variant="list.data.value.is_public ? 'success' : 'neutral'" size="sm">
          {{ list.data.value.is_public ? 'Herkese açık' : 'Gizli' }}
        </BaseBadge>
      </div>
      <p class="text-sm text-muted">
        <RouterLink :to="`/u/${list.data.value.owner.username}`" class="font-medium text-fg hover:underline">
          {{ list.data.value.owner.display_name || list.data.value.owner.username }}
        </RouterLink>
        · {{ list.data.value.item_count }} öğe
      </p>
      <p v-if="list.data.value.description" class="text-sm text-fg">{{ list.data.value.description }}</p>
    </div>

    <div class="flex flex-wrap items-center gap-3">
      <BaseButton variant="ghost" @click="share">Paylaş</BaseButton>
      <template v-if="isOwner">
        <BaseButton variant="ghost" @click="editModalOpen = true">Düzenle</BaseButton>
        <BaseButton v-if="!reordering" variant="ghost" :disabled="list.data.value.items.length < 2" @click="startReorder">Sırala</BaseButton>
        <template v-else>
          <BaseButton :loading="reorderMutation.isPending.value" @click="saveOrder">Sırayı kaydet</BaseButton>
          <BaseButton variant="secondary" @click="cancelReorder">Vazgeç</BaseButton>
        </template>
        <BaseButton variant="danger" @click="removeList">Sil</BaseButton>
      </template>
    </div>

    <EmptyState
      v-if="displayItems.length === 0"
      title="Bu liste henüz boş"
      message="Bir film, dizi veya kitap sayfasından “Özel Listeye Ekle” ile öğe ekleyebilirsin."
    />
    <div v-else class="grid grid-cols-2 gap-x-4 gap-y-6 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
      <div v-for="(item, index) in displayItems" :key="item.content.external_id" class="flex flex-col gap-1.5">
        <PosterCard :content="item.content" size="md" class="!w-full" />

        <div v-if="reordering" class="flex items-center justify-center gap-2">
          <button type="button" class="rounded-lg border border-border px-2 py-1 text-xs disabled:opacity-30" :disabled="index === 0" @click="moveUp(index)">↑</button>
          <button
            type="button"
            class="rounded-lg border border-border px-2 py-1 text-xs disabled:opacity-30"
            :disabled="index === displayItems.length - 1"
            @click="moveDown(index)"
          >
            ↓
          </button>
        </div>

        <template v-else>
          <div v-if="isOwner && editingNoteFor === item.content.id" class="flex flex-col gap-1">
            <textarea v-model="noteDraft" rows="2" maxlength="300" class="w-full rounded-lg border border-border bg-surface-1 p-1.5 text-xs text-fg" />
            <div class="flex gap-2">
              <button type="button" class="text-xs font-medium text-link hover:underline" @click="saveNote(item.content.id)">Kaydet</button>
              <button type="button" class="text-xs text-muted hover:text-fg" @click="editingNoteFor = null">Vazgeç</button>
            </div>
          </div>
          <p v-else-if="item.note" class="line-clamp-2 text-xs text-muted">{{ item.note }}</p>

          <div v-if="isOwner && editingNoteFor !== item.content.id" class="flex items-center gap-3 text-xs">
            <button type="button" class="text-muted hover:text-fg" @click="startEditNote(item)">{{ item.note ? 'Notu düzenle' : 'Not ekle' }}</button>
            <button type="button" class="text-muted hover:text-danger" @click="removeItem(item.content.id)">Kaldır</button>
          </div>
        </template>
      </div>
    </div>

    <ListFormModal v-model="editModalOpen" :list="list.data.value" />
  </div>
</template>
