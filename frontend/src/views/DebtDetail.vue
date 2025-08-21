<template>
  <div v-if="isLoading" class="text-center py-8">
    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
    <p class="mt-4 text-sm text-gray-500">Loading debt details...</p>
  </div>

  <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
    <div class="text-sm text-red-700">{{ error }}</div>
  </div>

  <div v-else-if="debt" class="max-w-4xl mx-auto space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <nav class="flex" aria-label="Breadcrumb">
          <ol class="flex items-center space-x-2">
            <li>
              <router-link to="/debts" class="text-gray-500 hover:text-gray-700">
                Debts
              </router-link>
            </li>
            <li>
              <ChevronRightIcon class="h-4 w-4 text-gray-400" />
            </li>
            <li class="text-gray-900 font-medium">
              {{ debt.description }}
            </li>
          </ol>
        </nav>
        <h1 class="mt-2 text-2xl font-bold text-gray-900">
          Debt Details
        </h1>
      </div>
      <div class="flex items-center space-x-3">
        <router-link
          :to="`/debts/${debt.id}/edit`"
          class="btn-secondary"
        >
          Edit
        </router-link>
        <button
          @click="showDeleteConfirm = true"
          class="btn-danger"
        >
          Delete
        </button>
      </div>
    </div>

    <!-- Main content -->
    <div class="grid grid-cols-1 gap-6 lg:grid-cols-3">
      <!-- Debt details -->
      <div class="lg:col-span-2">
        <div class="bg-white shadow rounded-lg">
          <div class="px-4 py-5 sm:p-6">
            <div class="space-y-6">
              <!-- Status and amount -->
              <div class="flex items-center justify-between">
                <div>
                  <h3 class="text-lg font-medium text-gray-900">
                    {{ debt.description }}
                  </h3>
                  <div class="mt-1 flex items-center">
                    <span :class="[
                      'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                      getStatusColor(debt.status)
                    ]">
                      {{ debt.status }}
                    </span>
                    <span
                      v-if="isOverdue && debt.status === 'pending'"
                      class="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800"
                    >
                      Overdue
                    </span>
                  </div>
                </div>
                <div class="text-right">
                  <p :class="[
                    'text-2xl font-bold',
                    debt.is_owed_to_me ? 'text-green-600' : 'text-red-600'
                  ]">
                    {{ debt.is_owed_to_me ? '+' : '-' }}KES {{ formatAmount(debt.amount) }}
                  </p>
                  <p class="text-sm text-gray-500">
                    {{ debt.is_owed_to_me ? 'Owed to me' : 'I owe' }}
                  </p>
                </div>
              </div>

              <!-- Details grid -->
              <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
                <div>
                  <dt class="text-sm font-medium text-gray-500">Debtor</dt>
                  <dd class="mt-1 text-sm text-gray-900">{{ debt.debtor }}</dd>
                </div>
                <div>
                  <dt class="text-sm font-medium text-gray-500">Creditor</dt>
                  <dd class="mt-1 text-sm text-gray-900">{{ debt.creditor }}</dd>
                </div>
                <div>
                  <dt class="text-sm font-medium text-gray-500">Due Date</dt>
                  <dd class="mt-1 text-sm text-gray-900">
                    {{ formatDate(debt.due_date) }}
                    <span v-if="daysUntilDue !== null" :class="[
                      'ml-2 text-xs',
                      daysUntilDue < 0 ? 'text-red-600' : 
                      daysUntilDue <= 7 ? 'text-yellow-600' : 'text-gray-500'
                    ]">
                      ({{ formatDaysUntilDue() }})
                    </span>
                  </dd>
                </div>
                <div>
                  <dt class="text-sm font-medium text-gray-500">Created</dt>
                  <dd class="mt-1 text-sm text-gray-900">{{ formatDate(debt.created_at) }}</dd>
                </div>
                <div>
                  <dt class="text-sm font-medium text-gray-500">Last Updated</dt>
                  <dd class="mt-1 text-sm text-gray-900">{{ formatDate(debt.updated_at) }}</dd>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Actions sidebar -->
      <div class="space-y-6">
        <!-- Quick actions -->
        <div class="bg-white shadow rounded-lg">
          <div class="px-4 py-5 sm:p-6">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
            <div class="space-y-3">
              <router-link
                :to="`/debts/${debt.id}/edit`"
                class="w-full btn-secondary flex items-center justify-center"
              >
                <PencilIcon class="h-4 w-4 mr-2" />
                Edit Debt
              </router-link>
              
              <button
                v-if="debt.status === 'pending'"
                @click="markAsPaid"
                :disabled="isUpdating"
                class="w-full btn-primary flex items-center justify-center disabled:opacity-50"
              >
                <CheckIcon class="h-4 w-4 mr-2" />
                {{ isUpdating ? 'Updating...' : 'Mark as Paid' }}
              </button>
              
              <button
                v-if="debt.status === 'pending'"
                @click="markAsCancelled"
                :disabled="isUpdating"
                class="w-full bg-gray-600 hover:bg-gray-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 flex items-center justify-center disabled:opacity-50"
              >
                <XMarkIcon class="h-4 w-4 mr-2" />
                {{ isUpdating ? 'Updating...' : 'Cancel Debt' }}
              </button>
            </div>
          </div>
        </div>

        <!-- Related info -->
        <div class="bg-white shadow rounded-lg">
          <div class="px-4 py-5 sm:p-6">
            <h3 class="text-lg font-medium text-gray-900 mb-4">Information</h3>
            <div class="space-y-3 text-sm">
              <div class="flex items-center justify-between">
                <span class="text-gray-500">Type:</span>
                <span class="font-medium">
                  {{ debt.is_owed_to_me ? 'Owed to me' : 'I owe' }}
                </span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-gray-500">Amount:</span>
                <span class="font-medium">KES {{ formatAmount(debt.amount) }}</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-gray-500">Status:</span>
                <span :class="[
                  'font-medium capitalize',
                  debt.status === 'paid' ? 'text-green-600' :
                  debt.status === 'pending' ? 'text-yellow-600' : 'text-gray-600'
                ]">
                  {{ debt.status }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete confirmation modal -->
    <div
      v-if="showDeleteConfirm"
      class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50"
      @click="showDeleteConfirm = false"
    >
      <div
        class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white"
        @click.stop
      >
        <div class="mt-3 text-center">
          <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
            <ExclamationTriangleIcon class="h-6 w-6 text-red-600" />
          </div>
          <h3 class="text-lg font-medium text-gray-900 mt-4">Delete Debt</h3>
          <div class="mt-2 px-7 py-3">
            <p class="text-sm text-gray-500">
              Are you sure you want to delete this debt record? This action cannot be undone.
            </p>
          </div>
          <div class="flex items-center justify-center space-x-3 mt-4">
            <button
              @click="showDeleteConfirm = false"
              class="btn-secondary"
            >
              Cancel
            </button>
            <button
              @click="handleDelete"
              :disabled="isDeleting"
              class="btn-danger disabled:opacity-50"
            >
              {{ isDeleting ? 'Deleting...' : 'Delete' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ChevronRightIcon,
  PencilIcon,
  CheckIcon,
  XMarkIcon,
  ExclamationTriangleIcon
} from '@heroicons/vue/24/outline'
import { useDebtStore } from '@/stores/debts'

interface Props {
  id?: string
}

const props = defineProps<Props>()

const route = useRoute()
const router = useRouter()
const debtStore = useDebtStore()

const showDeleteConfirm = ref(false)
const isUpdating = ref(false)
const isDeleting = ref(false)

const debtId = computed(() => props.id || route.params.id as string)
const debt = computed(() => debtStore.currentDebt)
const isLoading = computed(() => debtStore.isLoading)
const error = computed(() => debtStore.error)

const isOverdue = computed(() => {
  if (!debt.value || debt.value.status !== 'pending') return false
  const dueDate = new Date(debt.value.due_date)
  const now = new Date()
  now.setHours(0, 0, 0, 0)
  dueDate.setHours(0, 0, 0, 0)
  return dueDate < now
})

const daysUntilDue = computed(() => {
  if (!debt.value) return null
  const dueDate = new Date(debt.value.due_date)
  const now = new Date()
  now.setHours(0, 0, 0, 0)
  dueDate.setHours(0, 0, 0, 0)
  return Math.ceil((dueDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))
})

const formatAmount = (amount: number): string => {
  return amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    year: 'numeric',
    month: 'long', 
    day: 'numeric' 
  })
}

const formatDaysUntilDue = (): string => {
  const days = daysUntilDue.value
  if (days === null) return ''
  
  if (days < 0) {
    return `${Math.abs(days)} days overdue`
  } else if (days === 0) {
    return 'Due today'
  } else if (days === 1) {
    return 'Due tomorrow'
  } else {
    return `${days} days remaining`
  }
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

const markAsPaid = async () => {
  if (!debt.value) return
  
  isUpdating.value = true
  try {
    await debtStore.updateDebt(debt.value.id, { status: 'paid' } as any)
  } catch (error) {
    console.error('Error marking debt as paid:', error)
  } finally {
    isUpdating.value = false
  }
}

const markAsCancelled = async () => {
  if (!debt.value) return
  
  isUpdating.value = true
  try {
    await debtStore.updateDebt(debt.value.id, { status: 'cancelled' } as any)
  } catch (error) {
    console.error('Error cancelling debt:', error)
  } finally {
    isUpdating.value = false
  }
}

const handleDelete = async () => {
  if (!debt.value) return
  
  isDeleting.value = true
  try {
    await debtStore.deleteDebt(debt.value.id)
    router.push('/debts')
  } catch (error) {
    console.error('Error deleting debt:', error)
  } finally {
    isDeleting.value = false
    showDeleteConfirm.value = false
  }
}

onMounted(async () => {
  try {
    await debtStore.fetchDebtById(debtId.value as string)
  } catch (error) {
    console.error('Error loading debt:', error)
  }
})
</script>
