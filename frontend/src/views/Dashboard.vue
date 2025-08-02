<template>
  <div class="space-y-8">
    <!-- Welcome section -->
    <div class="bg-white overflow-hidden shadow rounded-lg">
      <div class="px-4 py-5 sm:p-6">
        <div class="flex items-center">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">
              Welcome back, {{ authStore.username }}!
            </h1>
            <p class="mt-1 text-sm text-gray-500">
              Here's an overview of your IOUs and debts.
            </p>
          </div>
          <div class="ml-auto">
            <router-link
              to="/ious/create"
              class="btn-primary"
            >
              New IOU
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Stats cards -->
    <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
      <!-- Total owed to me -->
      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                <CurrencyDollarIcon class="w-5 h-5 text-white" />
              </div>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">
                  Owed to me
                </dt>
                <dd class="text-lg font-medium text-gray-900">
                  ${{ formatAmount(totalOwedToMe) }}
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <!-- Total I owe -->
      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-red-500 rounded-md flex items-center justify-center">
                <BanknotesIcon class="w-5 h-5 text-white" />
              </div>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">
                  I owe
                </dt>
                <dd class="text-lg font-medium text-gray-900">
                  ${{ formatAmount(totalIOwe) }}
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <!-- Active IOUs -->
      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                <DocumentTextIcon class="w-5 h-5 text-white" />
              </div>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">
                  Active IOUs
                </dt>
                <dd class="text-lg font-medium text-gray-900">
                  {{ totalActiveIOUs }}
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <!-- Overdue items -->
      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-yellow-500 rounded-md flex items-center justify-center">
                <ExclamationTriangleIcon class="w-5 h-5 text-white" />
              </div>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">
                  Overdue
                </dt>
                <dd class="text-lg font-medium text-gray-900">
                  {{ totalOverdue }}
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent activity and upcoming due dates -->
    <div class="grid grid-cols-1 gap-8 lg:grid-cols-2">
      <!-- Recent IOUs -->
      <div class="bg-white shadow rounded-lg">
        <div class="px-4 py-5 sm:px-6 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <h3 class="text-lg leading-6 font-medium text-gray-900">
              Recent IOUs
            </h3>
            <router-link
              to="/ious"
              class="text-sm font-medium text-primary-600 hover:text-primary-500"
            >
              View all
            </router-link>
          </div>
        </div>
        <div class="px-4 py-5 sm:p-6">
          <div v-if="isLoading" class="text-center py-4">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
            <p class="mt-2 text-sm text-gray-500">Loading...</p>
          </div>
          <div v-else-if="recentIOUs.length === 0" class="text-center py-8">
            <DocumentTextIcon class="mx-auto h-12 w-12 text-gray-400" />
            <h3 class="mt-2 text-sm font-medium text-gray-900">No IOUs</h3>
            <p class="mt-1 text-sm text-gray-500">Get started by creating a new IOU.</p>
            <div class="mt-6">
              <router-link to="/ious/create" class="btn-primary">
                Create IOU
              </router-link>
            </div>
          </div>
          <div v-else class="space-y-3">
            <div
              v-for="iou in recentIOUs"
              :key="iou.id"
              class="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50"
            >
              <div class="flex-1">
                <p class="text-sm font-medium text-gray-900">
                  {{ iou.description }}
                </p>
                <p class="text-sm text-gray-500">
                  {{ iou.is_owed_to_me ? iou.debtor : iou.creditor }} • Due {{ formatDate(iou.due_date) }}
                </p>
              </div>
              <div class="text-right">
                <p :class="[
                  'text-sm font-medium',
                  iou.is_owed_to_me ? 'text-green-600' : 'text-red-600'
                ]">
                  {{ iou.is_owed_to_me ? '+' : '-' }}${{ formatAmount(iou.amount) }}
                </p>
                <span :class="[
                  'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                  getStatusColor(iou.status)
                ]">
                  {{ iou.status }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Upcoming due dates -->
      <div class="bg-white shadow rounded-lg">
        <div class="px-4 py-5 sm:px-6 border-b border-gray-200">
          <h3 class="text-lg leading-6 font-medium text-gray-900">
            Upcoming Due Dates
          </h3>
        </div>
        <div class="px-4 py-5 sm:p-6">
          <div v-if="upcomingDueDates.length === 0" class="text-center py-8">
            <CalendarIcon class="mx-auto h-12 w-12 text-gray-400" />
            <h3 class="mt-2 text-sm font-medium text-gray-900">No upcoming due dates</h3>
            <p class="mt-1 text-sm text-gray-500">All your IOUs are up to date.</p>
          </div>
          <div v-else class="space-y-3">
            <div
              v-for="item in upcomingDueDates"
              :key="item.id"
              class="flex items-center justify-between p-3 border border-gray-200 rounded-lg"
              :class="{ 'border-red-300 bg-red-50': isOverdue(item.due_date) }"
            >
              <div class="flex-1">
                <p class="text-sm font-medium text-gray-900">
                  {{ item.description }}
                </p>
                <p class="text-sm text-gray-500">
                  {{ item.is_owed_to_me ? item.debtor : item.creditor }}
                </p>
              </div>
              <div class="text-right">
                <p class="text-sm font-medium text-gray-900">
                  ${{ formatAmount(item.amount) }}
                </p>
                <p :class="[
                  'text-sm',
                  isOverdue(item.due_date) ? 'text-red-600 font-medium' : 'text-gray-500'
                ]">
                  {{ formatDueDate(item.due_date) }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import {
  CurrencyDollarIcon,
  BanknotesIcon,
  DocumentTextIcon,
  ExclamationTriangleIcon,
  CalendarIcon
} from '@heroicons/vue/24/outline'
import { useAuthStore } from '@/stores/auth'
import { useIOUStore } from '@/stores/ious'
import { useDebtStore } from '@/stores/debts'

const authStore = useAuthStore()
const iouStore = useIOUStore()
const debtStore = useDebtStore()

const isLoading = computed(() => iouStore.isLoading || debtStore.isLoading)

const totalOwedToMe = computed(() => 
  iouStore.totalOwedToMe + debtStore.totalOwedToMe
)

const totalIOwe = computed(() => 
  iouStore.totalIOwe + debtStore.totalIOwe
)

const totalActiveIOUs = computed(() => 
  iouStore.pendingIOUs.length + debtStore.pendingDebts.length
)

const totalOverdue = computed(() => 
  iouStore.overdueIOUs.length + debtStore.overdueDebts.length
)

const recentIOUs = computed(() => {
  const allItems = [...iouStore.ious, ...debtStore.debts]
  return allItems
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 5)
})

const upcomingDueDates = computed(() => {
  const allItems = [...iouStore.pendingIOUs, ...debtStore.pendingDebts]
  const now = new Date()
  const in30Days = new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000)
  
  return allItems
    .filter(item => {
      const dueDate = new Date(item.due_date)
      return dueDate <= in30Days
    })
    .sort((a, b) => new Date(a.due_date).getTime() - new Date(b.due_date).getTime())
    .slice(0, 5)
})

const formatAmount = (amount: number): string => {
  return amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

const formatDueDate = (dateString: string): string => {
  const date = new Date(dateString)
  const now = new Date()
  const diffInDays = Math.ceil((date.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))
  
  if (diffInDays < 0) {
    return `${Math.abs(diffInDays)} days overdue`
  } else if (diffInDays === 0) {
    return 'Due today'
  } else if (diffInDays === 1) {
    return 'Due tomorrow'
  } else {
    return `Due in ${diffInDays} days`
  }
}

const isOverdue = (dateString: string): boolean => {
  const date = new Date(dateString)
  const now = new Date()
  now.setHours(0, 0, 0, 0)
  date.setHours(0, 0, 0, 0)
  return date < now
}

const getStatusColor = (status: string): string => {
  switch (status) {
    case 'pending':
      return 'bg-yellow-100 text-yellow-800'
    case 'paid':
      return 'bg-green-100 text-green-800'
    case 'cancelled':
      return 'bg-gray-100 text-gray-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

onMounted(async () => {
  try {
    await Promise.all([
      iouStore.fetchIOUs(),
      debtStore.fetchDebts()
    ])
  } catch (error) {
    console.error('Error loading dashboard data:', error)
  }
})
</script>
