import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { notificationApi } from '@/services/api'
import type { Notification } from '@/types/api'

export const useNotificationStore = defineStore('notifications', () => {
  // State
  const notifications = ref<Notification[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const unreadNotifications = computed(() => 
    notifications.value.filter(notification => !notification.read)
  )
  
  const unreadCount = computed(() => unreadNotifications.value.length)
  
  const recentNotifications = computed(() => 
    notifications.value
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      .slice(0, 10)
  )

  // Actions
  const fetchNotifications = async () => {
    isLoading.value = true
    error.value = null
    
    try {
      const data = await notificationApi.getAll()
      notifications.value = data
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch notifications'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const markAsRead = async (id: number) => {
    try {
      const updatedNotification = await notificationApi.markAsRead(id)
      const index = notifications.value.findIndex(notification => notification.id === id)
      if (index !== -1) {
        notifications.value[index] = updatedNotification
      }
      return updatedNotification
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to mark notification as read'
      throw err
    }
  }

  const markAllAsRead = async () => {
    const unread = unreadNotifications.value
    for (const notification of unread) {
      try {
        await markAsRead(notification.id)
      } catch (err) {
        console.error('Error marking notification as read:', err)
      }
    }
  }

  const addNotification = (notification: Notification) => {
    notifications.value.unshift(notification)
  }

  const clearError = () => {
    error.value = null
  }

  return {
    // State
    notifications,
    isLoading,
    error,
    // Getters
    unreadNotifications,
    unreadCount,
    recentNotifications,
    // Actions
    fetchNotifications,
    markAsRead,
    markAllAsRead,
    addNotification,
    clearError
  }
})
