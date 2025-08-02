<template>
  <header class="bg-white shadow-sm border-b border-gray-200">
    <div class="flex items-center justify-between h-16 px-4 lg:px-6">
      <!-- Mobile menu button -->
      <button
        @click="$emit('toggleSidebar')"
        class="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100"
      >
        <Bars3Icon class="h-6 w-6" />
      </button>

      <!-- Page title -->
      <div class="flex-1 lg:flex lg:items-center lg:justify-between">
        <h1 class="text-xl font-semibold text-gray-900 ml-4 lg:ml-0">
          {{ pageTitle }}
        </h1>

        <!-- Right side actions -->
        <div class="flex items-center space-x-4">
          <!-- Notifications dropdown -->
          <div class="relative" ref="notificationsDropdown">
            <button
              @click="showNotifications = !showNotifications"
              class="relative p-2 text-gray-400 hover:text-gray-500 hover:bg-gray-100 rounded-full transition-colors duration-200"
            >
              <BellIcon class="h-6 w-6" />
              <span
                v-if="notificationStore.unreadCount > 0"
                class="absolute -top-1 -right-1 h-5 w-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center"
              >
                {{ notificationStore.unreadCount > 9 ? '9+' : notificationStore.unreadCount }}
              </span>
            </button>

            <!-- Notifications dropdown menu -->
            <div
              v-if="showNotifications"
              class="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border border-gray-200 z-50"
            >
              <div class="p-4 border-b border-gray-200">
                <div class="flex items-center justify-between">
                  <h3 class="text-lg font-medium text-gray-900">Notifications</h3>
                  <button
                    v-if="notificationStore.unreadCount > 0"
                    @click="markAllAsRead"
                    class="text-sm text-primary-600 hover:text-primary-500"
                  >
                    Mark all read
                  </button>
                </div>
              </div>
              
              <div class="max-h-80 overflow-y-auto">
                <div
                  v-if="notificationStore.recentNotifications.length === 0"
                  class="p-4 text-center text-gray-500"
                >
                  No notifications
                </div>
                <div
                  v-for="notification in notificationStore.recentNotifications"
                  :key="notification.id"
                  :class="[
                    'p-4 border-b border-gray-100 hover:bg-gray-50 cursor-pointer',
                    !notification.read && 'bg-blue-50'
                  ]"
                  @click="markAsRead(notification)"
                >
                  <div class="flex items-start">
                    <div class="flex-1">
                      <p class="text-sm font-medium text-gray-900">
                        {{ notification.title }}
                      </p>
                      <p class="text-sm text-gray-500 mt-1">
                        {{ notification.message }}
                      </p>
                      <p class="text-xs text-gray-400 mt-2">
                        {{ formatDate(notification.created_at) }}
                      </p>
                    </div>
                    <div
                      v-if="!notification.read"
                      class="h-2 w-2 bg-blue-500 rounded-full flex-shrink-0 mt-2"
                    ></div>
                  </div>
                </div>
              </div>
              
              <div class="p-4 border-t border-gray-200">
                <router-link
                  to="/notifications"
                  class="block w-full text-center text-sm text-primary-600 hover:text-primary-500"
                  @click="showNotifications = false"
                >
                  View all notifications
                </router-link>
              </div>
            </div>
          </div>

          <!-- User profile -->
          <div class="flex items-center text-sm">
            <span class="text-gray-700 hidden sm:block">
              {{ authStore.username }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { Bars3Icon, BellIcon } from '@heroicons/vue/24/outline'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notifications'
import type { Notification } from '@/types/api'

defineEmits<{
  toggleSidebar: []
}>()

const route = useRoute()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()

const showNotifications = ref(false)
const notificationsDropdown = ref<HTMLElement>()

const pageTitle = computed(() => {
  const routeName = route.name as string
  const titles: Record<string, string> = {
    'dashboard': 'Dashboard',
    'ious': 'IOUs',
    'iou-create': 'Create IOU',
    'iou-detail': 'IOU Details',
    'iou-edit': 'Edit IOU',
    'debts': 'Debts',
    'debt-create': 'Create Debt',
    'debt-detail': 'Debt Details',
    'debt-edit': 'Edit Debt',
    'notifications': 'Notifications',
    'profile': 'Profile'
  }
  return titles[routeName] || 'IOU Tracker'
})

const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  const now = new Date()
  const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60))
  
  if (diffInMinutes < 1) return 'Just now'
  if (diffInMinutes < 60) return `${diffInMinutes}m ago`
  
  const diffInHours = Math.floor(diffInMinutes / 60)
  if (diffInHours < 24) return `${diffInHours}h ago`
  
  const diffInDays = Math.floor(diffInHours / 24)
  if (diffInDays < 7) return `${diffInDays}d ago`
  
  return date.toLocaleDateString()
}

const markAsRead = async (notification: Notification) => {
  if (!notification.read) {
    try {
      await notificationStore.markAsRead(notification.id)
    } catch (error) {
      console.error('Error marking notification as read:', error)
    }
  }
}

const markAllAsRead = async () => {
  try {
    await notificationStore.markAllAsRead()
  } catch (error) {
    console.error('Error marking all notifications as read:', error)
  }
}

// Close notifications dropdown when clicking outside
const handleClickOutside = (event: Event) => {
  if (notificationsDropdown.value && !notificationsDropdown.value.contains(event.target as Node)) {
    showNotifications.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  // Fetch notifications on mount
  notificationStore.fetchNotifications()
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>
