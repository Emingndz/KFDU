<script setup lang="ts">
import { ref } from 'vue'
import { toast } from 'vue-sonner'
import { Heart, Settings } from 'lucide-vue-next'

import { useTheme } from '@/composables/useTheme'
import { useConfirm } from '@/composables/useConfirm'

import BaseButton from '@/components/ui/BaseButton.vue'
import BaseInput from '@/components/ui/BaseInput.vue'
import BaseTextarea from '@/components/ui/BaseTextarea.vue'
import BaseSelect from '@/components/ui/BaseSelect.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseTabs from '@/components/ui/BaseTabs.vue'
import BaseAvatar from '@/components/ui/BaseAvatar.vue'
import BaseBadge from '@/components/ui/BaseBadge.vue'
import BaseSkeleton from '@/components/ui/BaseSkeleton.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import ErrorState from '@/components/ui/ErrorState.vue'
import BaseSpinner from '@/components/ui/BaseSpinner.vue'

const { mode, options: themeOptions } = useTheme()
const { confirm } = useConfirm()

const textValue = ref('')
const textareaValue = ref('')
const selectValue = ref('')
const modalOpen = ref(false)
const activeTab = ref('genel')
const loadingDemo = ref(false)

async function onConfirmDemo() {
  const ok = await confirm({
    title: 'Emin misin?',
    message: 'Bu işlem geri alınamaz.',
    confirmText: 'Evet, sil',
    danger: true,
  })
  toast[ok ? 'success' : 'info'](ok ? 'Onaylandı' : 'Vazgeçildi')
}

function toggleLoadingDemo() {
  loadingDemo.value = true
  setTimeout(() => (loadingDemo.value = false), 1500)
}
</script>

<template>
  <div class="mx-auto max-w-4xl space-y-10 p-8">
    <header class="flex items-center justify-between">
      <h1 class="text-3xl font-bold">KFDU — Bileşen Vitrini</h1>
      <BaseSelect v-model="mode" :options="themeOptions.map((o) => ({ value: o.value, label: o.label }))" />
    </header>

    <section class="space-y-3">
      <h2 class="text-xl font-semibold">Butonlar</h2>
      <div class="flex flex-wrap items-center gap-3">
        <BaseButton variant="primary">Birincil</BaseButton>
        <BaseButton variant="secondary">İkincil</BaseButton>
        <BaseButton variant="ghost">Hayalet</BaseButton>
        <BaseButton variant="danger">Tehlike</BaseButton>
        <BaseButton variant="link">Bağlantı</BaseButton>
        <BaseButton :loading="loadingDemo" @click="toggleLoadingDemo">Yükleniyor demo</BaseButton>
        <BaseButton disabled>Devre dışı</BaseButton>
        <BaseButton size="sm">Küçük</BaseButton>
        <BaseButton size="lg">Büyük</BaseButton>
        <BaseButton>
          <template #icon><Heart class="size-4" /></template>
          İkonlu
        </BaseButton>
      </div>
    </section>

    <section class="space-y-3">
      <h2 class="text-xl font-semibold">Form elemanları</h2>
      <div class="grid gap-4 sm:grid-cols-2">
        <BaseInput v-model="textValue" label="Kullanıcı adı" hint="3-30 karakter" :maxlength="30" />
        <BaseInput label="Şifre" type="password" placeholder="••••••••" />
        <BaseInput label="Hatalı alan" error="Bu alan zorunlu" />
        <BaseSelect
          v-model="selectValue"
          label="Tür"
          placeholder="Seç"
          :options="[
            { value: 'action', label: 'Aksiyon' },
            { value: 'drama', label: 'Dram' },
          ]"
        />
        <BaseTextarea
          v-model="textareaValue"
          label="İnceleme"
          hint="En az 3 karakter"
          :maxlength="500"
          class="sm:col-span-2"
        />
      </div>
    </section>

    <section class="space-y-3">
      <h2 class="text-xl font-semibold">Rozet, iskelet, avatar</h2>
      <div class="flex flex-wrap items-center gap-3">
        <BaseBadge variant="movie">Film</BaseBadge>
        <BaseBadge variant="tv">Dizi</BaseBadge>
        <BaseBadge variant="book">Kitap</BaseBadge>
        <BaseBadge variant="success">★ 8.4</BaseBadge>
        <BaseBadge variant="danger">Hata</BaseBadge>
        <BaseAvatar name="Ada Lovelace" size="sm" />
        <BaseAvatar name="Kerem Yılmaz" size="md" />
        <BaseAvatar name="Zeynep Öz" size="lg" src="/broken-image.jpg" />
        <BaseSpinner />
      </div>
      <div class="flex gap-3">
        <BaseSkeleton class="h-24 w-16" rounded="lg" />
        <BaseSkeleton class="h-4 w-40" />
        <BaseSkeleton class="size-10" rounded="full" />
      </div>
    </section>

    <section class="space-y-3">
      <h2 class="text-xl font-semibold">Sekmeler</h2>
      <BaseTabs
        v-model="activeTab"
        :tabs="[
          { value: 'genel', label: 'Genel' },
          { value: 'kutuphane', label: 'Kütüphane' },
          { value: 'listeler', label: 'Listeler' },
        ]"
      />
      <p class="text-sm text-muted">Aktif sekme: {{ activeTab }}</p>
    </section>

    <section class="space-y-3">
      <h2 class="text-xl font-semibold">Modal ve onay</h2>
      <div class="flex gap-3">
        <BaseButton @click="modalOpen = true">Modal aç</BaseButton>
        <BaseButton variant="danger" @click="onConfirmDemo">
          <template #icon><Settings class="size-4" /></template>
          Onay iste
        </BaseButton>
      </div>
      <BaseModal v-model="modalOpen" title="Örnek modal">
        <p class="text-sm text-muted">Esc ile veya dışarı tıklayarak kapatabilirsin.</p>
        <template #footer>
          <BaseButton variant="secondary" @click="modalOpen = false">Kapat</BaseButton>
        </template>
      </BaseModal>
    </section>

    <section class="space-y-3">
      <h2 class="text-xl font-semibold">Durum bileşenleri</h2>
      <div class="rounded-card border border-border">
        <EmptyState title="Henüz hiçbir şey yok" message="Buraya içerik eklendiğinde görünecek." />
      </div>
      <div class="rounded-card border border-border">
        <ErrorState message="Sunucuya ulaşılamadı." @retry="toast.info('Tekrar deneniyor…')" />
      </div>
    </section>
  </div>
</template>
