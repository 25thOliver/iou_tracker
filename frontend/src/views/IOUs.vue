<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">IOUs</h1>
        <p class="mt-1 text-sm text-gray-500">
          Manage your IOUs and track who owes what.
        </p>
      </div>
      <div class="flex space-x-3">
        <router-link
          to="/ious/create"
          class="btn-primary"
        >
          Create IOU
        </router-link>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
      <div class="flex flex-wrap gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Filter by</label>
          <select
            v-model="filterType"
            class="input-field w-auto min-w-[120px]"
          >
            <option value="all">All IOUs</option>
            <option value="owed_to_me">Owed to me</option>
            <option value="i_owe">I owe</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
          <select
            v-model="filterStatus"
            class="input-field w-auto min-w-[120px]"
          >
            <option value="all">All statuses</option>
            <option value="pending">Pending</option>
            <option value="paid">Paid</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Search</label>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search IOUs..."
            class="input-field w-auto min-w-[200px]"
          />
        </div>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="iouStore.isLoading" class="text-center py-8">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
      <p class="mt-4 text-sm text-gray-500">Loading IOUs...</p>
    </div>

    <!-- Error state -->
    <div v-else-if="iouStore.error" class="bg-red-50 border border-red-200 rounded-lg p-4">
      <div class="text-sm text-red-700">
        {{ iouStore.error }}
      </div>
    </div>

    <!-- Empty state -->
    <div v-else-if="filteredIOUs.length === 0 && !searchQuery" class="text-center py-12">
      <DocumentTextIcon class="mx-auto h-12 w-12 text-gray-400" />
      <h3 class="mt-2 text-sm font-medium text-gray-900">No IOUs</h3>
      <p class="mt-1 text-sm text-gray-500">Get started by creating your first IOU.</p>
      <div class="mt-6">
        <router-link to="/ious/create" class="btn-primary">
          Create IOU
        </router-link>
      </div>
    </div>

    <!-- No search results -->
    <div v-else-if="filteredIOUs.length === 0 && searchQuery" class="text-center py-12">
      <MagnifyingGlassIcon class="mx-auto h-12 w-12 text-gray-400" />
      <h3 class="mt-2 text-sm font-medium text-gray-900">No results found</h3>
      <p class="mt-1 text-sm text-gray-500">Try adjusting your search or filters.</p>
    </div>

    <!-- IOUs list -->
    <div v-else class="bg-white shadow overflow-hidden sm:rounded-md">
      <ul class="divide-y divide-gray-200">
        <li v-for="iou in filteredIOUs" :key="iou.id">
          <router-link
            :to="`/ious/${iou.id}`"
            class="block hover:bg-gray-50 px-4 py-4 sm:px-6"
          >
            <div class="flex items-center justify-between">
              <div class="flex-1 min-w-0">
                <div class="flex items-center justify-between">
                  <p class="text-sm font-medium text-gray-900 truncate">
                    {{ iou.description }}
                  </p>
                  <div class="ml-2 flex-shrink-0 flex">
                    <span :class="[
                      'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                      getStatusColor(iou.status)
                    ]">
                      {{ iou.status }}
                    </span>
                  </div>
                </div>
                <div class="mt-2 flex items-center text-sm text-gray-500">
                  <div class="flex items-center">
                    <UserIcon class="flex-shrink-0 mr-1.5 h-4 w-4 text-gray-400" />
                    <span>
                      <span v-if="iou.is_owed_to_me">
                        <span class="font-medium text-gray-700">{{ iou.debtor }}</span> owes me
                      </span>
                      <span v-else>
                        I owe <span class="font-medium text-gray-700">{{ iou.creditor }}</span>
                      </span>
                    </span>
                  </div>
                  <div class="ml-6 flex items-center">
                    <CalendarIcon class="flex-shrink-0 mr-1.5 h-4 w-4 text-gray-400" />
                    <span>Due {{ formatDate(iou.due_date) }}</span>
                    <span
                      v-if="isOverdue(iou.due_date) && iou.status === 'pending'"
                      class="ml-2 text-red-600 font-medium"
                    >
                      (Overdue)
                    </span>
                  </div>
                </div>
              </div>
              <div class="ml-4 flex-shrink-0 text-right">
                <p :class="[
                  'text-lg font-medium',
                  iou.is_owed_to_me ? 'text-green-600' : 'text-red-600'
                ]">
                  {{ iou.is_owed_to_me ? '+' : '-' }}KSh {{ formatAmount(iou.amount) }}
                </p>
                <p class="text-sm text-gray-500">
                  {{ iou.is_owed_to_me ? 'Owed to me' : 'I owe' }}
                </p>
              </div>
            </div>
          </router-link>
        </li>
      </ul>
    </div>

    <!-- Summary -->
    <div v-if="filteredIOUs.length > 0" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 class="text-lg font-medium text-gray-900 mb-4">Summary</h3>
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div class="text-center">
          <p class="text-2xl font-bold text-green-600">
            KSh {{ formatAmount(summaryOwedToMe) }}
          </p>
          <p class="text-sm text-gray-500">Total owed to me</p>
        </div>
        <div class="text-center">
          <p class="text-2xl font-bold text-red-600">
            KSh {{ formatAmount(summaryIOwe) }}
          </p>
          <p class="text-sm text-gray-500">Total I owe</p>
        </div>
        <div class="text-center">
          <p class="text-2xl font-bold text-gray-900">
            {{ filteredIOUs.length }}
          </p>
          <p class="text-sm text-gray-500">Total IOUs</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import {
  DocumentTextIcon,
  MagnifyingGlassIcon,
  UserIcon,
  CalendarIcon
} from '@heroicons/vue/24/outline'
import { useIOUStore } from '@/stores/ious'

const iouStore = useIOUStore()

const filterType = ref('all')
const filterStatus = ref('all')
const searchQuery = ref('')

const filteredIOUs = computed(() => {
  let filtered = [...iouStore.ious]

  // Filter by type
  if (filterType.value === 'owed_to_me') {
    filtered = filtered.filter(iou => iou.is_owed_to_me)
  } else if (filterType.value === 'i_owe') {
    filtered = filtered.filter(iou => !iou.is_owed_to_me)
  }

  // Filter by status
  if (filterStatus.value !== 'all') {
    filtered = filtered.filter(iou => iou.status === filterStatus.value)
  }

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(iou =>
      iou.description.toLowerCase().includes(query) ||
      iou.debtor.toLowerCase().includes(query) ||
      iou.creditor.toLowerCase().includes(query)
    )
  }

  // Sort by due date (closest first) and then by creation date (newest first)
  return filtered.sort((a, b) => {
    if (a.status === 'pending' && b.status !== 'pending') return -1
    if (a.status !== 'pending' && b.status === 'pending') return 1

    const dueDateA = new Date(a.due_date).getTime()
    const dueDateB = new Date(b.due_date).getTime()
    if (dueDateA !== dueDateB) return dueDateA - dueDateB

    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  })
})

const summaryOwedToMe = computed(() =>
  filteredIOUs.value
    .filter(iou => iou.is_owed_to_me && iou.status === 'pending')
    .reduce((sum, iou) => sum + iou.amount, 0)
)

const summaryIOwe = computed(() =>
  filteredIOUs.value
    .filter(iou => !iou.is_owed_to_me && iou.status === 'pending')
    .reduce((sum, iou) => sum + iou.amount, 0)
)

const formatAmount = (amount: number): string => {
  return amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
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
    await iouStore.fetchIOUs()
  } catch (error) {
    console.error('Error loading IOUs:', error)
  }
})
</script>
