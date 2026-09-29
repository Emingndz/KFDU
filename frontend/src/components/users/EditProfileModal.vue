<script setup lang="ts">
import BaseModal from '@/components/ui/BaseModal.vue'
import ProfileForm from '@/components/users/ProfileForm.vue'

const open = defineModel<boolean>({ default: false })
</script>

<template>
  <BaseModal v-model="open" title="Profili düzenle">
    <ProfileForm @saved="open = false" />
  </BaseModal>
</template>
