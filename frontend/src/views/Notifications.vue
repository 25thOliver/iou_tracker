<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Notifications</h1>
        <p class="mt-1 text-sm text-gray-500">
          Stay updated with your IOU and debt activities.
        </p>
      </div>
      <div class="flex items-center space-x-3">
        <button
          v-if="notificationStore.unreadCount > 0"
          @click="markAllAsRead"
          :disabled="isMarkingAllRead"
          class="btn-secondary disabled:opacity-50"
        >
          {{ isMarkingAllRead ? 'Marking...' : 'Mark all as read' }}
        </button>
        <div class="text-sm text-gray-500">
          {{ notificationStore.unreadCount }} unread
        </div>
      </div>
    </div>

    <!-- Filter tabs -->
    <div class="border-b border-gray-200">
      <nav class="-mb-px flex space-x-8">
        <button
          v-for="tab in filterTabs"
          :key="tab.key"
          @click="activeFilter = tab.key"
          :class="[
            'whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm transition-colors duration-200',
            activeFilter === tab.key
              ? 'border-primary-500 text-primary-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          {{ tab.label }}
          <span
            v-if="tab.count > 0"
            :class="[
              'ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
              activeFilter === tab.key
                ? 'bg-primary-100 text-primary-800'
                : 'bg-gray-100 text-gray-800'
            ]"
          >
            {{ tab.count }}
          </span>
        </button>
      </nav>
    </div>

    <!-- Loading state -->
    <div v-if="notificationStore.isLoading" class="text-center py-8">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
      <p class="mt-4 text-sm text-gray-500">Loading notifications...</p>
    </div>

    <!-- Error state -->
    <div v-else-if="notificationStore.error" class="bg-red-50 border border-red-200 rounded-lg p-4">
      <div class="text-sm text-red-700">
        {{ notificationStore.error }}
      </div>
    </div>

    <!-- Empty state -->
    <div v-else-if="filteredNotifications.length === 0" class="text-center py-12">
      <BellIcon class="mx-auto h-12 w-12 text-gray-400" />
      <h3 class="mt-2 text-sm font-medium text-gray-900">
        {{ activeFilter === 'unread' ? 'No unread notifications' : 'No notifications' }}
      </h3>
      <p class="mt-1 text-sm text-gray-500">
        {{ activeFilter === 'unread' 
          ? 'All caught up! Check back later for new updates.' 
          : 'When you have IOUs and debts, you\'ll see notifications here.'
        }}
      </p>
    </div>

    <!-- Notifications list -->
    <div v-else class="space-y-3">
      <div
        v-for="notification in filteredNotifications"
        :key="notification.id"
        :class="[
          'bg-white rounded-lg shadow-sm border border-gray-200 p-4 transition-all duration-200 hover:shadow-md',
          !notification.read && 'border-l-4 border-l-primary-500 bg-blue-50'
        ]"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <component
                  :is="getNotificationIcon(notification.notification_type)"
                  :class="[
                    'h-5 w-5',
                    getNotificationIconColor(notification.notification_type)
                  ]"
                />
              </div>
              <div class="ml-3 flex-1">
                <h4 class="text-sm font-medium text-gray-900">
                  {{ notification.title }}
                </h4>
                <p class="mt-1 text-sm text-gray-600">
                  {{ notification.message }}
                </p>
                <div class="mt-2 flex items-center text-xs text-gray-500">
                  <span>{{ formatDate(notification.created_at) }}</span>
                  <span class="mx-2">•</span>
                  <span class="capitalize">{{ notification.notification_type.replace('_', ' ') }}</span>
                </div>
              </div>
            </div>
          </div>
          <div class="ml-4 flex items-center space-x-2">
            <div
              v-if="!notification.read"
              class="h-2 w-2 bg-primary-500 rounded-full flex-shrink-0"
              title="Unread"
            ></div>
            <button
              v-if="!notification.read"
              @click="markAsRead(notification)"
              class="text-sm text-primary-600 hover:text-primary-500 font-medium"
            >
              Mark as read
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Load more button -->
    <div v-if="hasMoreNotifications" class="text-center">
      <button
        @click="loadMoreNotifications"
        :disabled="isLoadingMore"
        class="btn-secondary disabled:opacity-50"
      >
        {{ isLoadingMore ? 'Loading...' : 'Load more notifications' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import {
  BellIcon,
  CurrencyDollarIcon,
  BanknotesIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon
} from '@heroicons/vue/24/outline'
import { useNotificationStore } from '@/stores/notifications'
import type { Notification } from '@/types/api'

const notificationStore = useNotificationStore()

const activeFilter = ref('all')
const isMarkingAllRead = ref(false)
const isLoadingMore = ref(false)
const hasMoreNotifications = ref(false) // This would be determined by pagination from API

const filterTabs = computed(() => [
  {
    key: 'all',
    label: 'All',
    count: notificationStore.notifications.length
  },
  {
    key: 'unread',
    label: 'Unread',
    count: notificationStore.unreadCount
  },
  {
    key: 'iou_created',
    label: 'IOU Created',
    count: notificationStore.notifications.filter(n => n.notification_type === 'iou_created').length
  },
  {
    key: 'debt_created',
    label: 'Debt Created',
    count: notificationStore.notifications.filter(n => n.notification_type === 'debt_created').length
  },
  {
    key: 'payment_reminder',
    label: 'Reminders',
    count: notificationStore.notifications.filter(n => n.notification_type === 'payment_reminder').length
  }
])

const filteredNotifications = computed(() => {
  let filtered = [...notificationStore.notifications]

  if (activeFilter.value === 'unread') {
    filtered = filtered.filter(n => !n.read)
  } else if (activeFilter.value !== 'all') {
    filtered = filtered.filter(n => n.notification_type === activeFilter.value)
  }

  return filtered.sort((a, b) => 
    new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  )
})

const getNotificationIcon = (type: string) => {
  switch (type) {
    case 'iou_created':
    case 'iou_updated':
      return CurrencyDollarIcon
    case 'debt_created':
    case 'debt_updated':
      return BanknotesIcon
    case 'payment_reminder':
      return ExclamationTriangleIcon
    default:
      return InformationCircleIcon
  }
}

const getNotificationIconColor = (type: string): string => {
  switch (type) {
    case 'iou_created':
    case 'iou_updated':
      return 'text-green-500'
    case 'debt_created':
    case 'debt_updated':
      return 'text-blue-500'
    case 'payment_reminder':
      return 'text-yellow-500'
    default:
      return 'text-gray-500'
  }
}

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
  
  return date.toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric',
    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
  })
}

const markAsRead = async (notification: Notification) => {
  try {
    await notificationStore.markAsRead(notification.id)
  } catch (error) {
    console.error('Error marking notification as read:', error)
  }
}

const markAllAsRead = async () => {
  isMarkingAllRead.value = true
  try {
    await notificationStore.markAllAsRead()
  } catch (error) {
    console.error('Error marking all notifications as read:', error)
  } finally {
    isMarkingAllRead.value = false
  }
}

const loadMoreNotifications = async () => {
  isLoadingMore.value = true
  try {
    // This would implement pagination in a real app
    // await notificationStore.fetchMoreNotifications()
    console.log('Load more notifications would be implemented here')
  } catch (error) {
    console.error('Error loading more notifications:', error)
  } finally {
    isLoadingMore.value = false
  }
}

let intervalId: number | undefined

const startBackgroundRefresh = () => {
  // Poll every 30s without blocking UI
  intervalId = window.setInterval(() => {
    notificationStore.fetchNotifications().catch((e) => {
      console.error('Background refresh failed:', e)
    })
  }, 30000)

  // Refresh when window regains focus
  window.addEventListener('focus', onWindowFocus)
}

const stopBackgroundRefresh = () => {
  if (intervalId) {
    clearInterval(intervalId)
    intervalId = undefined
  }
  window.removeEventListener('focus', onWindowFocus)
}

function onWindowFocus() {
  notificationStore.fetchNotifications().catch(() => {})
}

onMounted(async () => {
  try {
    if (notificationStore.notifications.length === 0) {
      await notificationStore.fetchNotifications()
    } else {
      // Soft refresh in background without blocking UI
      notificationStore.fetchNotifications().catch((e) => {
        console.error('Background refresh failed:', e)
      })
    }
    startBackgroundRefresh()
  } catch (error) {
    console.error('Error loading notifications:', error)
  }
})

onUnmounted(() => {
  stopBackgroundRefresh()
})
</script>
