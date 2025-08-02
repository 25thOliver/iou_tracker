<template>
  <!-- Mobile sidebar overlay -->
  <div
    v-if="isOpen"
    class="fixed inset-0 bg-gray-600 bg-opacity-75 z-40 lg:hidden"
    @click="$emit('close')"
  ></div>

  <!-- Sidebar -->
  <div
    :class="[
      'fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-xl transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0',
      isOpen ? 'translate-x-0' : '-translate-x-full'
    ]"
  >
    <!-- Sidebar header -->
    <div class="flex items-center justify-between h-16 px-4 border-b border-gray-200">
      <div class="flex items-center">
        <h1 class="text-xl font-bold text-gray-900">IOU Tracker</h1>
      </div>
      <button
        @click="$emit('close')"
        class="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100"
      >
        <XMarkIcon class="h-6 w-6" />
      </button>
    </div>

    <!-- Navigation -->
    <nav class="mt-8 px-4">
      <div class="space-y-1">
        <router-link
          v-for="item in navigation"
          :key="item.name"
          :to="item.href"
          :class="[
            'group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors duration-200',
            $route.name === item.routeName
              ? 'bg-primary-100 text-primary-700'
              : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
          ]"
          @click="$emit('close')"
        >
          <component
            :is="item.icon"
            :class="[
              'mr-3 h-6 w-6 flex-shrink-0',
              $route.name === item.routeName
                ? 'text-primary-500'
                : 'text-gray-400 group-hover:text-gray-500'
            ]"
          />
          {{ item.name }}
          <span
            v-if="item.badge"
            class="ml-auto inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800"
          >
            {{ item.badge }}
          </span>
        </router-link>
      </div>
    </nav>

    <!-- User info -->
    <div class="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200">
      <div class="flex items-center">
        <div class="flex-shrink-0">
          <div class="h-8 w-8 rounded-full bg-primary-500 flex items-center justify-center">
            <span class="text-sm font-medium text-white">
              {{ userInitials }}
            </span>
          </div>
        </div>
        <div class="ml-3 flex-1 min-w-0">
          <p class="text-sm font-medium text-gray-900 truncate">
            {{ authStore.username }}
          </p>
        </div>
        <button
          @click="handleLogout"
          class="ml-3 flex-shrink-0 p-1 text-gray-400 hover:text-gray-500"
          title="Logout"
        >
          <ArrowRightOnRectangleIcon class="h-5 w-5" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  HomeIcon,
  CurrencyDollarIcon,
  BanknotesIcon,
  BellIcon,
  UserIcon,
  XMarkIcon,
  ArrowRightOnRectangleIcon
} from '@heroicons/vue/24/outline'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notifications'

interface Props {
  isOpen: boolean
}

defineProps<Props>()
defineEmits<{
  close: []
}>()

const router = useRouter()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()

const navigation = computed(() => [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: HomeIcon,
    routeName: 'dashboard'
  },
  {
    name: 'IOUs',
    href: '/ious',
    icon: CurrencyDollarIcon,
    routeName: 'ious'
  },
  {
    name: 'Debts',
    href: '/debts',
    icon: BanknotesIcon,
    routeName: 'debts'
  },
  {
    name: 'Notifications',
    href: '/notifications',
    icon: BellIcon,
    routeName: 'notifications',
    badge: notificationStore.unreadCount > 0 ? notificationStore.unreadCount : undefined
  },
  {
    name: 'Profile',
    href: '/profile',
    icon: UserIcon,
    routeName: 'profile'
  }
])

const userInitials = computed(() => {
  const username = authStore.username
  return username ? username.substring(0, 2).toUpperCase() : 'U'
})

const handleLogout = async () => {
  try {
    await authStore.logout()
    router.push('/login')
  } catch (error) {
    console.error('Logout error:', error)
  }
}
</script>
