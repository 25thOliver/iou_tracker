<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Debts</h1>
        <p class="mt-1 text-sm text-gray-500">
          Manage your debts and track financial obligations.
        </p>
      </div>
      <div class="flex space-x-3">
        <router-link
          to="/debts/create"
          class="btn-primary"
        >
          Create Debt
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
            <option value="all">All Debts</option>
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
            placeholder="Search debts..."
            class="input-field w-auto min-w-[200px]"
          />
        </div>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="debtStore.isLoading" class="text-center py-8">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
      <p class="mt-4 text-sm text-gray-500">Loading debts...</p>
    </div>

    <!-- Error state -->
    <div v-else-if="debtStore.error" class="bg-red-50 border border-red-200 rounded-lg p-4">
      <div class="text-sm text-red-700">
        {{ debtStore.error }}
      </div>
    </div>

    <!-- Empty state -->
    <div v-else-if="filteredDebts.length === 0 && !searchQuery" class="text-center py-12">
      <BanknotesIcon class="mx-auto h-12 w-12 text-gray-400" />
      <h3 class="mt-2 text-sm font-medium text-gray-900">No Debts</h3>
      <p class="mt-1 text-sm text-gray-500">Get started by creating your first debt record.</p>
      <div class="mt-6">
        <router-link to="/debts/create" class="btn-primary">
          Create Debt
        </router-link>
      </div>
    </div>

    <!-- No search results -->
    <div v-else-if="filteredDebts.length === 0 && searchQuery" class="text-center py-12">
      <MagnifyingGlassIcon class="mx-auto h-12 w-12 text-gray-400" />
      <h3 class="mt-2 text-sm font-medium text-gray-900">No results found</h3>
      <p class="mt-1 text-sm text-gray-500">Try adjusting your search or filters.</p>
    </div>

    <!-- Debts list -->
    <div v-else class="bg-white shadow overflow-hidden sm:rounded-md">
      <ul class="divide-y divide-gray-200">
        <li v-for="debt in filteredDebts" :key="debt.id">
          <router-link
            :to="`/debts/${debt.id}`"
            class="block hover:bg-gray-50 px-4 py-4 sm:px-6"
          >
            <div class="flex items-center justify-between">
              <div class="flex-1 min-w-0">
                <div class="flex items-center justify-between">
                  <p class="text-sm font-medium text-gray-900 truncate">
                    {{ debt.description }}
                  </p>
                  <div class="ml-2 flex-shrink-0 flex">
                    <span :class="[
                      'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                      getStatusColor(debt.status)
                    ]">
                      {{ debt.status }}
                    </span>
                  </div>
                </div>
                <div class="mt-2 flex items-center text-sm text-gray-500">
                  <div class="flex items-center">
                    <UserIcon class="flex-shrink-0 mr-1.5 h-4 w-4 text-gray-400" />
                    <span>{{ debt.is_owed_to_me ? debt.debtor : debt.creditor }}</span>
                  </div>
                  <div class="ml-6 flex items-center">
                    <CalendarIcon class="flex-shrink-0 mr-1.5 h-4 w-4 text-gray-400" />
                    <span>Due {{ formatDate(debt.due_date) }}</span>
                    <span
                      v-if="isOverdue(debt.due_date) && debt.status === 'pending'"
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
                  debt.is_owed_to_me ? 'text-green-600' : 'text-red-600'
                ]">
                  {{ debt.is_owed_to_me ? '+' : '-' }}${{ formatAmount(debt.amount) }}
                </p>
                <p class="text-sm text-gray-500">
                  {{ debt.is_owed_to_me ? 'Owed to me' : 'I owe' }}
                </p>
              </div>
            </div>
          </router-link>
        </li>
      </ul>
    </div>

    <!-- Summary -->
    <div v-if="filteredDebts.length > 0" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 class="text-lg font-medium text-gray-900 mb-4">Summary</h3>
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div class="text-center">
          <p class="text-2xl font-bold text-green-600">
            ${{ formatAmount(summaryOwedToMe) }}
          </p>
          <p class="text-sm text-gray-500">Total owed to me</p>
        </div>
        <div class="text-center">
          <p class="text-2xl font-bold text-red-600">
            ${{ formatAmount(summaryIOwe) }}
          </p>
          <p class="text-sm text-gray-500">Total I owe</p>
        </div>
        <div class="text-center">
          <p class="text-2xl font-bold text-gray-900">
            {{ filteredDebts.length }}
          </p>
          <p class="text-sm text-gray-500">Total debts</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import {
  BanknotesIcon,
  MagnifyingGlassIcon,
  UserIcon,
  CalendarIcon
} from '@heroicons/vue/24/outline'
import { useDebtStore } from '@/stores/debts'

const debtStore = useDebtStore()

const filterType = ref('all')
const filterStatus = ref('all')
const searchQuery = ref('')

const filteredDebts = computed(() => {
  let filtered = [...debtStore.debts]

  // Filter by type
  if (filterType.value === 'owed_to_me') {
    filtered = filtered.filter(debt => debt.is_owed_to_me)
  } else if (filterType.value === 'i_owe') {
    filtered = filtered.filter(debt => !debt.is_owed_to_me)
  }

  // Filter by status
  if (filterStatus.value !== 'all') {
    filtered = filtered.filter(debt => debt.status === filterStatus.value)
  }

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(debt =>
      debt.description.toLowerCase().includes(query) ||
      debt.debtor.toLowerCase().includes(query) ||
      debt.creditor.toLowerCase().includes(query)
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
  filteredDebts.value
    .filter(debt => debt.is_owed_to_me && debt.status === 'pending')
    .reduce((sum, debt) => sum + debt.amount, 0)
)

const summaryIOwe = computed(() => 
  filteredDebts.value
    .filter(debt => !debt.is_owed_to_me && debt.status === 'pending')
    .reduce((sum, debt) => sum + debt.amount, 0)
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
    await debtStore.fetchDebts()
  } catch (error) {
    console.error('Error loading debts:', error)
  }
})
</script>
