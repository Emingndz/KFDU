<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { onClickOutside } from '@vueuse/core'
import { toast } from 'vue-sonner'
import { Check, ListPlus, Plus } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { useAddListItem, useCreateList, useMyLists, useRemoveListItem } from '@/api/lists'
import type { CatalogContentType } from '@/api/catalog'
import BaseButton from '@/components/ui/BaseButton.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseSpinner from '@/components/ui/BaseSpinner.vue'

const props = defineProps<{ type: CatalogContentType; externalId: string; contentId: number }>()

const auth = useAuthStore()
const router = useRouter()

const open = ref(false)
const menuRef = ref<HTMLElement | null>(null)
onClickOutside(menuRef, () => (open.value = false))

const lists = useMyLists(props.type, props.externalId)
const addItem = useAddListItem()
const removeItem = useRemoveListItem()
const createList = useCreateList()

const creatingNew = ref(false)
const newListTitle = ref('')
const pendingListId = ref<number | null>(null)

function openMenu() {
  if (!auth.isAuthenticated) {
    toast.info('Bunun için giriş yapmalısın')
    void router.push({ path: '/giris', query: { redirect: router.currentRoute.value.fullPath } })
    return
  }
  open.value = !open.value
}

async function toggle(listId: number, contains: boolean) {
  pendingListId.value = listId
  try {
    if (contains) {
      await removeItem.mutateAsync({ listId, contentId: props.contentId })
    } else {
      await addItem.mutateAsync({ listId, payload: { type: props.type, external_id: props.externalId, note: null } })
    }
  } catch {
    toast.error('Bir şeyler ters gitti, tekrar dene')
  } finally {
    pendingListId.value = null
  }
}

async function submitNewList() {
  const title = newListTitle.value.trim()
  if (!title) return
  try {
    const created = await createList.mutateAsync({ title, description: null, is_public: true })
    await addItem.mutateAsync({ listId: created.id, payload: { type: props.type, external_id: props.externalId, note: null } })
    newListTitle.value = ''
    creatingNew.value = false
    toast.success('Liste oluşturuldu ve eklendi')
  } catch {
    toast.error('Liste oluşturulamadı')
  }
}
</script>

<template>
  <div ref="menuRef" class="relative">
    <BaseButton variant="secondary" @click="openMenu">
      <template #icon><ListPlus class="size-4" /></template>
      Listeye ekle
    </BaseButton>

    <div
      v-if="open"
      class="absolute right-0 z-10 mt-2 w-64 rounded-card border border-border bg-surface p-2 shadow-xl"
    >
      <div v-if="lists.isPending.value" class="flex justify-center py-4">
        <BaseSpinner />
      </div>
      <p v-else-if="lists.isError.value" class="px-2 py-2 text-sm text-danger">Listeler yüklenemedi.</p>
      <template v-else>
        <p v-if="(lists.data.value ?? []).length === 0" class="px-2 py-2 text-sm text-muted">
          Henüz listen yok.
        </p>
        <button
          v-for="list in lists.data.value"
          :key="list.id"
          type="button"
          class="flex w-full items-center justify-between rounded-lg px-2 py-2 text-left text-sm hover:bg-surface-2 disabled:opacity-60"
          :disabled="pendingListId === list.id"
          @click="toggle(list.id, list.contains)"
        >
          <span class="truncate text-fg">{{ list.title }}</span>
          <Check v-if="list.contains" class="size-4 shrink-0 text-link" />
        </button>
      </template>

      <div class="mt-1 border-t border-border pt-2">
        <form v-if="creatingNew" class="flex items-center gap-2" @submit.prevent="submitNewList">
          <BaseInput v-model="newListTitle" placeholder="Liste adı" class="flex-1" />
          <BaseButton type="submit" size="sm" :loading="createList.isPending.value">Ekle</BaseButton>
        </form>
        <button
          v-else
          type="button"
          class="flex w-full items-center gap-2 rounded-lg px-2 py-2 text-left text-sm text-link hover:bg-surface-2"
          @click="creatingNew = true"
        >
          <Plus class="size-4" />
          Yeni liste
        </button>
      </div>
    </div>
  </div>
</template>
