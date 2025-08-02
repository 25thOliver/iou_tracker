<template>
  <div class="max-w-2xl mx-auto">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-gray-900">
        {{ isEdit ? 'Edit Debt' : 'Create New Debt' }}
      </h1>
      <p class="mt-1 text-sm text-gray-500">
        {{ isEdit ? 'Update the details of your debt.' : 'Fill in the details to create a new debt record.' }}
      </p>
    </div>

    <div class="bg-white shadow sm:rounded-lg">
      <form @submit.prevent="handleSubmit" class="space-y-6 p-6">
        <!-- Error message -->
        <div
          v-if="error"
          class="rounded-md bg-red-50 p-4 border border-red-200"
        >
          <div class="text-sm text-red-700">
            {{ error }}
          </div>
        </div>

        <!-- Description -->
        <div>
          <label for="description" class="block text-sm font-medium text-gray-700">
            Description *
          </label>
          <div class="mt-1">
            <input
              id="description"
              v-model="form.description"
              type="text"
              required
              placeholder="e.g., Credit card debt, Student loan, Mortgage payment"
              class="input-field"
              :class="{ 'border-red-300': errors.description }"
            />
            <p v-if="errors.description" class="mt-1 text-sm text-red-600">
              {{ errors.description }}
            </p>
          </div>
        </div>

        <!-- Amount -->
        <div>
          <label for="amount" class="block text-sm font-medium text-gray-700">
            Amount ($) *
          </label>
          <div class="mt-1">
            <input
              id="amount"
              v-model.number="form.amount"
              type="number"
              step="0.01"
              min="0"
              required
              placeholder="0.00"
              class="input-field"
              :class="{ 'border-red-300': errors.amount }"
            />
            <p v-if="errors.amount" class="mt-1 text-sm text-red-600">
              {{ errors.amount }}
            </p>
          </div>
        </div>

        <!-- Who owes whom -->
        <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
          <!-- Debtor -->
          <div>
            <label for="debtor" class="block text-sm font-medium text-gray-700">
              Debtor (who owes money) *
            </label>
            <div class="mt-1">
              <input
                id="debtor"
                v-model="form.debtor"
                type="text"
                required
                placeholder="Name of person who owes"
                class="input-field"
                :class="{ 'border-red-300': errors.debtor }"
              />
              <p v-if="errors.debtor" class="mt-1 text-sm text-red-600">
                {{ errors.debtor }}
              </p>
            </div>
          </div>

          <!-- Creditor -->
          <div>
            <label for="creditor" class="block text-sm font-medium text-gray-700">
              Creditor (who is owed money) *
            </label>
            <div class="mt-1">
              <input
                id="creditor"
                v-model="form.creditor"
                type="text"
                required
                placeholder="Name of person who is owed"
                class="input-field"
                :class="{ 'border-red-300': errors.creditor }"
              />
              <p v-if="errors.creditor" class="mt-1 text-sm text-red-600">
                {{ errors.creditor }}
              </p>
            </div>
          </div>
        </div>

        <!-- Due date -->
        <div>
          <label for="due_date" class="block text-sm font-medium text-gray-700">
            Due Date *
          </label>
          <div class="mt-1">
            <input
              id="due_date"
              v-model="form.due_date"
              type="date"
              required
              class="input-field"
              :class="{ 'border-red-300': errors.due_date }"
            />
            <p v-if="errors.due_date" class="mt-1 text-sm text-red-600">
              {{ errors.due_date }}
            </p>
          </div>
        </div>

        <!-- Helper text -->
        <div class="bg-blue-50 rounded-lg p-4">
          <div class="flex">
            <InformationCircleIcon class="h-5 w-5 text-blue-400 mt-0.5" />
            <div class="ml-3">
              <h3 class="text-sm font-medium text-blue-800">
                About Debts vs IOUs
              </h3>
              <div class="mt-2 text-sm text-blue-700">
                <p>
                  Debts are typically more formal financial obligations (loans, credit cards, etc.), 
                  while IOUs are usually casual agreements between friends or family.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Action buttons -->
        <div class="flex items-center justify-end space-x-3 pt-6">
          <router-link
            to="/debts"
            class="btn-secondary"
          >
            Cancel
          </router-link>
          <button
            type="submit"
            :disabled="isLoading"
            class="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="isLoading" class="flex items-center">
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ isEdit ? 'Updating...' : 'Creating...' }}
            </span>
            <span v-else>
              {{ isEdit ? 'Update Debt' : 'Create Debt' }}
            </span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { InformationCircleIcon } from '@heroicons/vue/24/outline'
import { useDebtStore } from '@/stores/debts'
import type { DebtCreate } from '@/types/api'

interface Props {
  id?: string
}

const props = defineProps<Props>()

const router = useRouter()
const route = useRoute()
const debtStore = useDebtStore()

const isEdit = computed(() => !!props.id || !!route.params.id)
const debtId = computed(() => props.id || route.params.id as string)

const form = reactive<DebtCreate>({
  description: '',
  amount: 0,
  debtor: '',
  creditor: '',
  due_date: ''
})

const errors = ref<Record<string, string>>({})
const error = ref<string | null>(null)
const isLoading = ref(false)

const validateForm = (): boolean => {
  errors.value = {}
  
  if (!form.description.trim()) {
    errors.value.description = 'Description is required'
  }
  
  if (!form.amount || form.amount <= 0) {
    errors.value.amount = 'Amount must be greater than 0'
  }
  
  if (!form.debtor.trim()) {
    errors.value.debtor = 'Debtor name is required'
  }
  
  if (!form.creditor.trim()) {
    errors.value.creditor = 'Creditor name is required'
  }
  
  if (!form.due_date) {
    errors.value.due_date = 'Due date is required'
  } else {
    const dueDate = new Date(form.due_date)
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    
    if (dueDate < today) {
      errors.value.due_date = 'Due date cannot be in the past'
    }
  }
  
  return Object.keys(errors.value).length === 0
}

const handleSubmit = async () => {
  if (!validateForm()) return
  
  isLoading.value = true
  error.value = null
  
  try {
    if (isEdit.value) {
      await debtStore.updateDebt(parseInt(debtId.value), form)
    } else {
      await debtStore.createDebt(form)
    }
    
    router.push('/debts')
  } catch (err: any) {
    console.error('Error saving debt:', err)
    error.value = err.response?.data?.message || `Failed to ${isEdit.value ? 'update' : 'create'} debt`
    
    // Handle field-specific errors
    if (err.response?.data?.errors) {
      errors.value = err.response.data.errors
    }
  } finally {
    isLoading.value = false
  }
}

const loadDebtForEdit = async () => {
  if (!isEdit.value) return
  
  try {
    const debt = await debtStore.fetchDebtById(parseInt(debtId.value))
    if (debt) {
      form.description = debt.description
      form.amount = debt.amount
      form.debtor = debt.debtor
      form.creditor = debt.creditor
      form.due_date = debt.due_date.split('T')[0] // Convert to YYYY-MM-DD format
    }
  } catch (err: any) {
    console.error('Error loading debt:', err)
    error.value = 'Failed to load debt data'
  }
}

onMounted(() => {
  // Set default due date to next month
  if (!isEdit.value) {
    const nextMonth = new Date()
    nextMonth.setMonth(nextMonth.getMonth() + 1)
    form.due_date = nextMonth.toISOString().split('T')[0]
  } else {
    loadDebtForEdit()
  }
})
</script>
