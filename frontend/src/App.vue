<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <AppLayout v-if="isAuthenticated" />
    <router-view v-else />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useAuthStore } from './stores/auth'
import AppLayout from './components/layout/AppLayout.vue'

const authStore = useAuthStore()

const isAuthenticated = computed(() => authStore.isAuthenticated)

onMounted(() => {
  // Load user from storage if available
  authStore.loadUserFromStorage()
  
  // If user is authenticated, refresh user data
  if (authStore.isAuthenticated) {
    authStore.getCurrentUser()
  }
})
</script>
